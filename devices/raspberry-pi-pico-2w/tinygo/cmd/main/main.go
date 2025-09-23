package main

import (
	"context"
	"math"
	"os"
	"time"

	"github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal"
	internalbno08x "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/bno08x"
	internalescmotor "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/escmotor"
	internalledonboard "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/led/onboard"
	internalservo "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/servo"
	internalswitch "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/switch"
	internalusbcdc "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/usbcdc"
	tinygobuffers "github.com/ralvarezdev/tinygo-buffers"
	tinygoerrors "github.com/ralvarezdev/tinygo-errors"
	// tinygologger "github.com/ralvarezdev/tinygo-logger"
)

const (
	// receivingMessageTimeout defines the maximum time to wait for receiving messages.
	receivingMessageTimeout = 5 * time.Second

	// sendBNO08XDataInterval defines the interval to send BNO08X data.
	sendBNO08XDataInterval = 20 * time.Millisecond

	// noMessageReceivedDelay is the time to sleep if no message is received.
	noMessageReceivedDelay = 2 * time.Millisecond

	// readMessageTimeout defines the timeout duration for reading messages.
	readMessageTimeout = 5 * time.Second
)

var (
	// failedToWaitForSwitchPressMessage is the message printed when waiting for switch press fails.
	failedToWaitForSwitchPressMessage = []byte("Failed to wait for switch press:")

	// switchOnEvent is called when the switch is pressed to initialize communication and provide visual feedback.
	switchOnEvent func() tinygoerrors.ErrorCode

	// lastMessageReceivedTime holds the timestamp of the last received message.
	lastMessageReceivedTime time.Time

	// lastBNO08XSentTime last sent time for BNO08X data
	lastBNO08XSentTime time.Time

	// newMessage is the newly received message.
	newMessage internalusbcdc.IncomingMessage
)

// stopAndCenter stops the ESC motor and centers the servo.
func stopAndCenter() {
	if err := internalescmotor.ESCMotorHandler.Stop(); err != tinygoerrors.ErrorCodeNil {
		internalusbcdc.USBCDCHandler.SendErrorMessage(err)
	}

	if err := internalservo.ServoHandler.SetAngleToCenter(); err != tinygoerrors.ErrorCodeNil {
		internalusbcdc.USBCDCHandler.SendErrorMessage(err)
	}
}

// updateLoop continuously updates the BNO08X sensor data, motor commands, and servo commands.
//
// Parameters:
//
// ctx: The context to manage the lifecycle of the update loop
func updateLoop(ctx context.Context) {
	for {
		select {
		case <-ctx.Done():
			return
		default:
			internalbno08x.UARTRVC.Update()
			time.Sleep(internalbno08x.Interval)
		}
	}
}

func init() {
	// Initialize the switch on event
	switchOnEvent = internalswitch.SwitchOnEventGenerator(
		internalusbcdc.USBCDCHandler,
		internalledonboard.OnBoardHandler,
	)
}

func main() {
	for {
		// Create a context to manage the lifecycle of the update loop
		ctx, cancel := context.WithCancel(context.Background())

		// Stop ESC motor and center servo before waiting for switch press
		stopAndCenter()

		// Add goroutine for update loop
		go updateLoop(ctx)

		// Wait for switch press
		if err := internalswitch.SwitchHandler.Wait(switchOnEvent); err != tinygoerrors.ErrorCodeNil {
			internal.Logger.ErrorMessageWithErrorCode(
				failedToWaitForSwitchPressMessage,
				err,
				true,
			)
			os.Exit(1)
		}

		// Reset the last message received time
		lastMessageReceivedTime = time.Now()

		// Set the exit condition to False
		toExit := false
		for !toExit {
			// Log memory status
			// tinygologger.DebugMemory(internal.Logger)

			// Check if the last message received time exceeds the timeout
			if time.Since(lastMessageReceivedTime) >= receivingMessageTimeout {
				toExit = true

				// Send a timeout error message
				internalusbcdc.USBCDCHandler.SendErrorMessage(internalusbcdc.ErrorCodeUSBCDCReceivingMessageTimeoutReached)

				// Stop the motor and center the servo
				stopAndCenter()
				break
			}

			// Send BNO08X data at defined intervals
			if time.Since(lastBNO08XSentTime) >= sendBNO08XDataInterval {
				// Get the Euler degrees from the BNO08X sensor
				eulerDegrees := internalbno08x.UARTRVC.GetEulerDegrees()

				// Send the Euler degrees messages via USB CDC
				if err := internalusbcdc.USBCDCHandler.SendBNO08XEulerDegreesMessages(eulerDegrees); err != tinygoerrors.ErrorCodeNil {
					internalusbcdc.USBCDCHandler.SendErrorMessage(err)
				}

				// Log the euler degrees values
				// internal.PrintEulerDegrees(eulerDegrees)

				// Update the last sent time
				lastBNO08XSentTime = time.Now()
			}

			// Check if a new message has arrived
			hasNewMessageArrived := internalusbcdc.USBCDCHandler.IsAvailableToRead()
			if !hasNewMessageArrived {
				time.Sleep(noMessageReceivedDelay)
				continue
			}

			// Read a message with a timeout
			message, err := internalusbcdc.USBCDCHandler.ReadMessage(readMessageTimeout)
			if err != tinygoerrors.ErrorCodeNil {
				internalusbcdc.USBCDCHandler.SendErrorMessage(err)
				continue
			}
			newMessage = message

			// Reset the last message received time if messages are received
			lastMessageReceivedTime = time.Now()

			// Handle specific message categories
			switch newMessage.Category {
			case internalusbcdc.IncomingCategoryServoAngleCenter, internalusbcdc.IncomingCategoryServoAngleToLeft, internalusbcdc.IncomingCategoryServoAngleToRight:
				// Check if the servo angle should be retrieved from the message
				var angle float64
				if message.Category != internalusbcdc.IncomingCategoryServoAngleCenter {
					// Get angle percentage from message content
					signedAngle, err := tinygobuffers.BytesToFloat64(message.Data)
					if err != tinygoerrors.ErrorCodeNil {
						internalusbcdc.USBCDCHandler.SendErrorMessage(err)
						continue
					}
					angle = math.Abs(signedAngle)
				}

				// Send start feedback message
				if err := internalusbcdc.USBCDCHandler.SendServoAngleStartMessage(); err != tinygoerrors.ErrorCodeNil {
					internalusbcdc.USBCDCHandler.SendErrorMessage(err)
					continue
				}

				// Set the servo angle based on the received message
				switch newMessage.Category {
				case internalusbcdc.IncomingCategoryServoAngleCenter:
					if err := internalservo.ServoHandler.SetAngleToCenter(); err != tinygoerrors.ErrorCodeNil {
						internalusbcdc.USBCDCHandler.SendErrorMessage(err)
					}
				case internalusbcdc.IncomingCategoryServoAngleToLeft:
					if err := internalservo.ServoHandler.SetAngleToLeft(uint16(angle * float64(internalservo.MaxLeftAngle))); err != tinygoerrors.ErrorCodeNil {
						internalusbcdc.USBCDCHandler.SendErrorMessage(err)
					}
				case internalusbcdc.IncomingCategoryServoAngleToRight:
					if err := internalservo.ServoHandler.SetAngleToRight(uint16(angle * float64(internalservo.MaxRightAngle))); err != tinygoerrors.ErrorCodeNil {
						internalusbcdc.USBCDCHandler.SendErrorMessage(err)
					}
				}

				// Send feedback message
				if err := internalusbcdc.USBCDCHandler.SendServoAngleEndMessage(); err != tinygoerrors.ErrorCodeNil {
					internalusbcdc.USBCDCHandler.SendErrorMessage(err)
				}
			case internalusbcdc.IncomingCategoryMotorSpeedStop, internalusbcdc.IncomingCategoryMotorSpeedForward, internalusbcdc.IncomingCategoryMotorSpeedBackward:
				// Check if the motor speed should be retrieved from the message
				var speed float64
				if message.Category != internalusbcdc.IncomingCategoryMotorSpeedStop {
					// Get speed percentage from message content
					signedSpeed, err := tinygobuffers.BytesToFloat64(message.Data)
					if err != tinygoerrors.ErrorCodeNil {
						internalusbcdc.USBCDCHandler.SendErrorMessage(err)
						continue
					}
					speed = math.Abs(signedSpeed)
				}

				// Send start feedback message
				if err := internalusbcdc.USBCDCHandler.SendMotorSpeedStartMessage(); err != tinygoerrors.ErrorCodeNil {
					internalusbcdc.USBCDCHandler.SendErrorMessage(err)
					continue
				}

				// Set the motor speed based on the received message
				switch newMessage.Category {
				case internalusbcdc.IncomingCategoryMotorSpeedStop:
					if err := internalescmotor.ESCMotorHandler.Stop(); err != tinygoerrors.ErrorCodeNil {
						internalusbcdc.USBCDCHandler.SendErrorMessage(err)
					}
				case internalusbcdc.IncomingCategoryMotorSpeedForward:
					if err := internalescmotor.ESCMotorHandler.SetSpeedForward(speed); err != tinygoerrors.ErrorCodeNil {
						internalusbcdc.USBCDCHandler.SendErrorMessage(err)
					}
				case internalusbcdc.IncomingCategoryMotorSpeedBackward:
					if err := internalescmotor.ESCMotorHandler.SetSpeedBackward(speed); err != tinygoerrors.ErrorCodeNil {
						internalusbcdc.USBCDCHandler.SendErrorMessage(err)
					}
				}

				// Send feedback message
				if err := internalusbcdc.USBCDCHandler.SendMotorSpeedEndMessage(); err != tinygoerrors.ErrorCodeNil {
					internalusbcdc.USBCDCHandler.SendErrorMessage(err)
				}
			case internalusbcdc.IncomingCategoryStatus:
				// Get the first byte of the message content
				if len(newMessage.Data) < 1 {
					internalusbcdc.USBCDCHandler.SendErrorMessage(internalusbcdc.ErrorCodeUSBCDCInvalidIncomingMessageDataLength)
					continue
				}

				// Get the status from the message content
				status, err := internalusbcdc.IncomingStatusFromUint8(newMessage.Data[0])
				if err != tinygoerrors.ErrorCodeNil {
					internalusbcdc.USBCDCHandler.SendErrorMessage(err)
					continue
				}

				switch status {
				case internalusbcdc.IncomingStatusHeartbeat:
					if err := internalusbcdc.USBCDCHandler.SendHeartbeatMessage(); err != tinygoerrors.ErrorCodeNil {
						internalusbcdc.USBCDCHandler.SendErrorMessage(err)
					}
				case internalusbcdc.IncomingStatusOK:
					internalusbcdc.USBCDCHandler.SendErrorMessage(internalusbcdc.ErrorCodeUSBCDCReceivedUnexpectedConfirmationMessage)
					continue
				case internalusbcdc.IncomingStatusStop:
					// Set the exit condition to True
					toExit = true

					// Stop the motor and center the servo
					stopAndCenter()

					// Send a confirmation message to the serial communication
					if err := internalusbcdc.USBCDCHandler.SendConfirmationMessage(); err != tinygoerrors.ErrorCodeNil {
						internalusbcdc.USBCDCHandler.SendErrorMessage(err)
					}
				}
			}
		}

		// Cancel the update loop context to stop the goroutine
		cancel()
	}
}
