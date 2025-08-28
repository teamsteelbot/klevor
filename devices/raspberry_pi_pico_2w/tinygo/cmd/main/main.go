package main

import (
	"context"
	"errors"
	"fmt"
	"time"

	internalbno08x "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/bno08x"
	internalescmotor "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/escmotor"
	internalledonboard "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/led/onboard"
	internalservo "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/servo"
	internalswitch "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/switch"
	internalusbcdc "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/usbcdc"
	internalusbcdcenums "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/usbcdc/enums"
	"golang.org/x/sync/errgroup"
)

const (
	// initializationTimeout defines the maximum time allowed for initialization tasks.
	initializationTimeout = 2 * time.Second

	// stopTimeout defines the maximum time allowed for stopping tasks.
	stopTimeout = 3 * time.Second

	// updateTimeout defines the maximum time allowed for update tasks.
	updateTimeout = 1 * time.Second

	// receivingMessageTimeout defines the maximum time to wait for receiving messages.
	receivingMessageTimeout = 1 * time.Second

	// updateMotorAndServoTimeout defines the maximum time allowed for updating motor speed and servo angle.
	updateMotorAndServoTimeout = 500 * time.Millisecond
)

var (
	// switchOnEvent is called when the switch is pressed to initialize communication and provide visual feedback.
	switchOnEvent func() error

	// incomingMessages is a slice to hold incoming messages from USB CDC.
	incomingMessages *[]internalusbcdc.IncomingMessage

	// lastMessageReceivedTime holds the timestamp of the last received message.
	lastMessageReceivedTime time.Time

	// lastBNO08XResetTime holds the timestamp of the last BNO08x reset.
	lastBNO08XResetTime time.Time

	// receivedMotorsSpeedMessage indicates if a motor speed message was received in the current cycle.
	receivedMotorsSpeedMessage *internalusbcdc.IncomingMessage

	// receivedServoAngleMessage holds the last received servo angle message.
	receivedServoAngleMessage *internalusbcdc.IncomingMessage

	// motorSpeed holds the desired motor speed.
	motorSpeed uint16

	// servoAngle holds the desired servo angle.
	servoAngle uint16
)

func init() {
	switchOnEvent = internalswitch.SwitchOnEventGenerator(
		internalusbcdc.USBCDCHandler,
		internalledonboard.OnBoardHandler,
	)
}

// stopAndCenter stops the ESC motor and centers the servo concurrently within a specified timeout.
//
// Parameters:
//
// timeout: The maximum duration to wait for both operations to complete.
//
// Returns:
//
// An error if either operation fails or the timeout is reached.
func stopAndCenter(timeout time.Duration) error {
	// Context with timeout
	ctx, cancel := context.WithTimeout(
		context.Background(),
		timeout,
	)
	g, ctx := errgroup.WithContext(ctx)

	// ESC motor stop
	g.Go(
		func() error {
			// Respect cancellation if long-running
			select {
			case <-ctx.Done():
				return ctx.Err()
			default:
			}
			return internalescmotor.ESCMotorHandler.Stop()
		},
	)

	// Servo center
	g.Go(
		func() error {
			select {
			case <-ctx.Done():
				return ctx.Err()
			default:
			}
			return internalservo.ServoHandler.SetAngleToCenter()
		},
	)

	// Wait for both; handle first error (if any)
	err := g.Wait()
	cancel()
	return err
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
}

func main() {
	for {
		// Stop ESC motor and center servo before waiting for switch press
		if err := stopAndCenter(initializationTimeout); err != nil {
			panic(
				fmt.Errorf(
					"error stopping esc motor and centering servo: %w",
					err,
				),
			)
		}

		// Wait for switch press
		if err := internalswitch.SwitchHandler.Wait(switchOnEvent); err != nil {
			panic(fmt.Errorf("error waiting for switch press: %w", err))
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

			// Create context with timeout for update routines
			ctx, cancel := context.WithTimeout(
				context.Background(),
				updateTimeout,
			)
			g, ctx := errgroup.WithContext(ctx)

			// Update BNO08x quaternion
			g.Go(
				func() error {
					// Respect cancellation if long-running
					select {
					case <-ctx.Done():
						return ctx.Err()
					default:
					}
					// Placeholder for BNO08x update logic
					return internalbno08x.BNO08XHandler.Update()
				},
			)

			// Receive USB CDC messages
			g.Go(
				func() error {
					// Respect cancellation if long-running
					select {
					case <-ctx.Done():
						return ctx.Err()
					default:
					}
					// Receive messages
					msgs, err := internalusbcdc.USBCDCHandler.ReceiveMessages()
					if err != nil {
						return err
					}
					incomingMessages = msgs
					return nil
				},
			)

			// Wait for both; handle first error (if any)
			if err := g.Wait(); err != nil {
				sendErrorMessage(err)
			}
			cancel()

			// Check if there are incoming messages
			if incomingMessages == nil {
				continue
			}

			// Process incoming messages
			if len(*incomingMessages) == 0 {
				// If no messages were received, check if the timeout has been reached
				if !lastMessageReceivedTime.IsZero() && time.Since(lastMessageReceivedTime) > receivingMessageTimeout {
					sendErrorMessage(errors.New("no messages received within the timeout period"))
				}
			} else {
				// Reset the last message received time if messages are received
				lastMessageReceivedTime = time.Now()
			}

			// Process each incoming message in reversed order
			for idx := len(*incomingMessages) - 1; idx >= 0; idx-- {
				msg := (*incomingMessages)[idx]

				// Check if is a heartbeat message
				if msg.IsEqual(internalusbcdc.IncomingHeartbeatMessage) {
					continue
				}

				// Check if is a stop message
				if msg.IsEqual(internalusbcdc.IncomingStopMessage) {
					// Set the exit condition to True
					toExit = true

					// Stop the motor and center the servo
					if err := stopAndCenter(stopTimeout); err != nil {
						sendErrorMessage(
							fmt.Errorf(
								"error stopping esc motor and centering servo: %w",
								err,
							),
						)
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
					break
				}

				// Check if the message is to set motor speed or servo angle
				if msg.Category.IsAMotorCategory() {
					// If a motor speed message was already processed, skip this one
					if receivedMotorsSpeedMessage != nil {
						continue
					}
					receivedMotorsSpeedMessage = &msg
				} else if msg.Category.IsAServoCategory() {
					// If a servo angle message was already processed, skip this one
					if receivedServoAngleMessage != nil {
						continue
					}
					receivedServoAngleMessage = &msg
				} else {
					sendErrorMessage(
						fmt.Errorf(
							"unknown message category: %v",
							msg.Category,
						),
					)
				}
			}

			// Check if the exit flag is set
			if toExit {
				// Break the loop if the exit flag is set
				break
			}

			// Check if we have received either or both motor speed and servo angle messages
			if receivedMotorsSpeedMessage != nil || receivedServoAngleMessage != nil {
				// Create the context for setting motor speed and servo angle
				ctx, cancel = context.WithTimeout(
					context.Background(),
					updateMotorAndServoTimeout,
				)
				g, ctx = errgroup.WithContext(ctx)

				// Add the set motor speed routine if a motor speed message was received
				if receivedMotorsSpeedMessage != nil {
					g.Go(
						func() error {
							// Respect cancellation if long-running
							select {
							case <-ctx.Done():
								return ctx.Err()
							default:
							}

							// Check if the motor speed should be retrieved from the message
							if receivedMotorsSpeedMessage.Category != internalusbcdcenums.IncomingCategoryMotorSpeedStop {
								// Get int16 speed from message content
								speed, err := receivedMotorsSpeedMessage.GetContentAsUint16()
								if err != nil {
									return fmt.Errorf(
										"invalid motor speed value: %w",
										err,
									)
								}
								motorSpeed = speed
							}

							// Check the motor speed category
							switch receivedMotorsSpeedMessage.Category {
							case internalusbcdcenums.IncomingCategoryMotorSpeedStop:
								return internalescmotor.ESCMotorHandler.Stop()
							case internalusbcdcenums.IncomingCategoryMotorSpeedForward:
								return internalescmotor.ESCMotorHandler.SetSpeedForward(motorSpeed)
							case internalusbcdcenums.IncomingCategoryMotorSpeedBackward:
								return internalescmotor.ESCMotorHandler.SetSpeedBackward(motorSpeed)
							default:
								return fmt.Errorf(
									"unknown motor speed category: %v",
									receivedMotorsSpeedMessage.Category,
								)
							}
						},
					)
				}

				// Add the set servo angle routine if a servo angle message was received
				if receivedServoAngleMessage != nil {
					g.Go(
						func() error {
							// Respect cancellation if long-running
							select {
							case <-ctx.Done():
								return ctx.Err()
							default:
							}

							// Check if the servo angle should be retrieved from the message
							if receivedServoAngleMessage.Category != internalusbcdcenums.IncomingCategoryServoAngleCenter {
								// Get uint16 angle from message content
								angle, err := receivedServoAngleMessage.GetContentAsUint16()
								if err != nil {
									return fmt.Errorf(
										"invalid servo angle value: %w",
										err,
									)
								}
								servoAngle = angle
							}

							// Check the servo angle category
							switch receivedServoAngleMessage.Category {
							case internalusbcdcenums.IncomingCategoryServoAngleCenter:
								return internalservo.ServoHandler.SetAngleToCenter()
							case internalusbcdcenums.IncomingCategoryServoAngleToLeft:
								return internalservo.ServoHandler.SetAngleToLeft(servoAngle)
							case internalusbcdcenums.IncomingCategoryServoAngleToRight:
								return internalservo.ServoHandler.SetAngleToRight(servoAngle)
							default:
								return fmt.Errorf(
									"unknown servo angle category: %v",
									receivedServoAngleMessage.Category,
								)
							}
						},
					)
				}

				// Wait for both; handle first error (if any)
				if err := g.Wait(); err != nil {
					sendErrorMessage(err)
				}
				cancel()
			}

			// Reset the variables for the next iteration
			receivedMotorsSpeedMessage = nil
			receivedServoAngleMessage = nil
		}
	}
}
