package main

import (
	"errors"
	"time"

	internalbno08x "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/bno08x"
	internalescmotor "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/escmotor"
	internalledonboard "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/led/onboard"
	internalservo "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/servo"
	internalswitch "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/switch"
	internalusbcdc "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/usbcdc"
	//internalusbcdcenums "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/usbcdc/enums"
	"golang.org/x/sync/errgroup"
)

const (
	// receivingMessageTimeout defines the maximum time to wait for receiving messages.
	receivingMessageTimeout = 5 * time.Second
)

var (
	// OutgoingMaxMotorSpeedMessage is the outgoing message to send the maximum motor speed
	OutgoingMaxMotorSpeedMessage = internalusbcdc.NewOutgoingMessageFromUint16Content(
		internalusbcdcenums.OutgoingCategoryMaxMotorSpeedValue,
		internalescmotor.MaxSpeed,
	)

	// OutgoingMaxServoDirectionMessage is the outgoing message to send the maximum servo direction
	OutgoingMaxServoDirectionMessage = internalusbcdc.NewOutgoingMessageFromUint16Content(
		internalusbcdcenums.OutgoingCategoryMaxServoDirectionValue,
		internalservo.MaxAngle,
	)

	// switchOnEvent is called when the switch is pressed to initialize communication and provide visual feedback.
	switchOnEvent func() error

	// lastMessageReceivedTime holds the timestamp of the last received message.
	lastMessageReceivedTime time.Time

	// lastBNO08XResetTime holds the timestamp of the last BNO08x reset.
	lastBNO08XResetTime time.Time

	// receivedMotorsSpeedMessage indicates if a motor speed message was received in the current cycle.
	receivedMotorsSpeedMessage *internalusbcdc.IncomingMessage

	// receivedServoDirectionMessage holds the last received servo angle message.
	receivedServoDirectionMessage *internalusbcdc.IncomingMessage
)

// stopAndCenter stops the ESC motor and centers the servo concurrently.
//
// Returns:
//
// An error if either operation fails.
func stopAndCenter() error {
	g := &errgroup.Group{}

	// ESC motor stop
	g.Go(
		internalescmotor.ESCMotorHandler.Stop,
	)

	// Servo center
	g.Go(
		internalservo.ServoHandler.SetDirectionToCenter,
	)

	// Wait for both; handle first error (if any)
	if err := g.Wait(); err != nil {
		return fmt.Errorf(
			"error stopping esc motor and centering servo: %w",
			err,
		)
	}
	return nil
}

// sendErrorMessage sends an error message via USB CDC if there is an error to be sent.
func sendErrorMessage(err error) {
	err = internalusbcdc.USBCDCHandler.SendErrorMessage(err)
	if err != nil {
		panic(fmt.Errorf("error sending error message: %w", err))
	}
}

func init() {
	// Set the last reset time
	lastBNO08XResetTime = time.Now()

	// Initialize the switch on event
	switchOnEvent = internalswitch.SwitchOnEventGenerator(
		internalusbcdc.USBCDCHandler,
		internalledonboard.OnBoardHandler,
	)
}

func main() {
	for {
		// Stop ESC motor and center servo before waiting for switch press
		if err := stopAndCenter(); err != nil {
			sendErrorMessage(err)
			continue
		}

		// Wait for switch press
		if err := internalswitch.SwitchHandler.Wait(switchOnEvent); err != nil {
			sendErrorMessage(fmt.Errorf("error waiting for switch press: %w", err))
			continue
		}

		// Set the exit condition to False
		toExit := false
		for !toExit {
			// Check if the BNO08x needs to be reset
			if time.Since(lastBNO08XResetTime) > internalbno08x.ResetBNO08XInterval {
				if err := internalbno08x.BNO08XHandler.Reset(); err != nil {
					sendErrorMessage(
						fmt.Errorf(
							"error resetting BNO08x: %w",
							err,
						),
					)
				} else {
					lastBNO08XResetTime = time.Now()
				}
			}

			// Create the group for concurrent tasks
			g := &errgroup.Group{}

			// Update BNO08x quaternion
			g.Go(
				internalbno08x.BNO08XHandler.Update,
			)

			// Receive USB CDC messages
			g.Go(
				internalusbcdc.USBCDCHandler.Update,
			)

			// Wait for both; handle first error (if any)
			if err := g.Wait(); err != nil {
				sendErrorMessage(err)
			}

			// Check if there are incoming messages
			incomingMessages := internalusbcdc.USBCDCHandler.GetIncomingMessages()
			if incomingMessages == nil || len(*incomingMessages) == 0 {
				// If no messages were received, check if the timeout has been reached
				if !lastMessageReceivedTime.IsZero() && time.Since(lastMessageReceivedTime) > receivingMessageTimeout {
					sendErrorMessage(errors.New("no messages received within the timeout period"))
				}
				continue
			}

			// Reset the last message received time if messages are received
			lastMessageReceivedTime = time.Now()

			// Process each incoming message in reversed order
			for idx := len(*incomingMessages) - 1; idx >= 0; idx-- {
				// Check if the exit flag is set
				if toExit {
					break
				}

				// Get the message
				message := (*incomingMessages)[idx]

				// Check if the message is nil
				if message == nil {
					continue
				}

				// Handle specific message categories
				switch message.Category {
				case internalusbcdcenums.IncomingCategoryGetMaxMotorSpeedValue:
					if err := internalusbcdc.USBCDCHandler.SendMessage(OutgoingMaxMotorSpeedMessage); err != nil {
						sendErrorMessage(
							fmt.Errorf(
								"error sending max motor speed message: %w",
								err,
							),
						)
					}
				case internalusbcdcenums.IncomingCategoryGetMaxServoDirectionValue:
					if err := internalusbcdc.USBCDCHandler.SendMessage(OutgoingMaxServoDirectionMessage); err != nil {
						sendErrorMessage(
							fmt.Errorf(
								"error sending max servo direction message: %w",
								err,
							),
						)
					}
				case internalusbcdcenums.IncomingCategoryStatus:
					// Check if it's a start message
					status, err := internalusbcdcenums.IncomingStatusFromString(message.Content)
					if err != nil {
						sendErrorMessage(fmt.Errorf("failed to parse status message content: %w", err))
					}

					switch status {
					case internalusbcdcenums.IncomingStatusHeartbeat:
						break
					case internalusbcdcenums.IncomingStatusOK:
						sendErrorMessage(
							errors.New("received unexpected OK status message"),
						)
					case internalusbcdcenums.IncomingStatusStop:
						// Set the exit condition to True
						toExit = true

						// Stop the motor and center the servo
						if err := stopAndCenter(); err != nil {
							sendErrorMessage(err)
						}

						// Send a confirmation message to the serial communication
						if err := internalusbcdc.USBCDCHandler.SendConfirmationMessage(); err != nil {
							sendErrorMessage(
								fmt.Errorf(
									"error sending confirmation message: %w",
									err,
								),
							)
						}
					}
				default:
					// Check if the message is to set motor speed or servo angle
					if message.Category.IsAMotorCategory() {
						// If a motor speed message was already processed, skip this one
						if receivedMotorsSpeedMessage != nil {
							continue
						}
						receivedMotorsSpeedMessage = &message
					} else if message.Category.IsAServoCategory() {
						// If a servo angle message was already processed, skip this one
						if receivedServoDirectionMessage != nil {
							continue
						}
						receivedServoDirectionMessage = &message
					} else {
						sendErrorMessage(
							fmt.Errorf(
								"unknown message category: %v",
								message.Category,
							),
						)
					}
				}
			}

			// Break the loop if the exit flag is set
			if toExit {
				break
			}

			// Check if we have received either or both motor speed and servo angle messages
			if receivedMotorsSpeedMessage != nil || receivedServoDirectionMessage != nil {
				// Create the context for setting motor speed and servo angle
				g = &errgroup.Group{}

				// Add the set motor speed routine if a motor speed message was received
				if receivedMotorsSpeedMessage != nil {
					g.Go(
						func() error {
							return internalescmotor.ESCMotorHandler.SetSpeedBasedOnReceivedMessage(receivedMotorsSpeedMessage)
						},
					)
				}

				// Add the set servo angle routine if a servo angle message was received
				if receivedServoDirectionMessage != nil {
					g.Go(
						func() error {
							return internalservo.ServoHandler.SetDirectionBasedOnReceivedMessage(receivedServoDirectionMessage)
						},
					)
				}

				// Wait for both; handle first error (if any)
				if err := g.Wait(); err != nil {
					sendErrorMessage(err)
				}
			}

			// Reset the variables for the next iteration
			receivedMotorsSpeedMessage = nil
			receivedServoDirectionMessage = nil
		}
	}
}
