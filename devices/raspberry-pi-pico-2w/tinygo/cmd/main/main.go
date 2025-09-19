package main

import (
	"os"
	"runtime"
	"time"

	"github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal"
	internalbno08x "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/bno08x"
	internalescmotor "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/escmotor"
	internalledonboard "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/led/onboard"
	internalservo "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/servo"
	internalswitch "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/switch"
	internalusbcdc "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/usbcdc"
	tinygoerrors "github.com/ralvarezdev/tinygo-errors"
	// tinygologger "github.com/ralvarezdev/tinygo-logger"
)

const (
	// receivingMessageTimeout defines the maximum time to wait for receiving messages.
	receivingMessageTimeout = 5 * time.Second

	// sendBNO08XDataInterval defines the interval to send BNO08X data.
	sendBNO08XDataInterval = 50 * time.Millisecond

	// noMessageReceivedDelay is the time to sleep if no message is received.
	noMessageReceivedDelay = 10 * time.Millisecond

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

// bno08xUpdateLoop continuously updates the BNO08X sensor data.
func bno08xUpdateLoop() {
	for {
		// Update the BNO08X sensor data
		internalbno08x.UARTRVC.Update()
		time.Sleep(internalbno08x.Interval)
		runtime.Gosched()
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
		// Stop ESC motor and center servo before waiting for switch press
		stopAndCenter()

		// Wait for switch press
		if err := internalswitch.SwitchHandler.Wait(switchOnEvent); err != tinygoerrors.ErrorCodeNil {
			internal.Logger.ErrorMessageWithErrorCode(
				failedToWaitForSwitchPressMessage,
				err,
				true,
			)
			os.Exit(1)
		}

		// Add goroutine for sending the BNO08X updates
		go bno08xUpdateLoop()

		// Reset the last message received time
		lastMessageReceivedTime = time.Now()

		// Last sent time for BNO08X data
		lastBNO08XSentTime := time.Now()

		// Set the exit condition to False
		toExit := false
		for !toExit {
			// Log memory status
			// tinygologger.DebugMemory(internal.Logger)

			if time.Since(lastBNO08XSentTime) >= sendBNO08XDataInterval {
				// Get the Euler degrees from the BNO08X sensor
				eulerDegrees := internalbno08x.UARTRVC.GetEulerDegrees()

				// Send the Euler degrees messages via USB CDC
				if err := internalusbcdc.USBCDCHandler.SendBNO08XEulerDegreesMessages(eulerDegrees); err != tinygoerrors.ErrorCodeNil {
					internalusbcdc.USBCDCHandler.SendErrorMessage(err)
				}

				// Update the last sent time
				lastBNO08XSentTime = time.Now()
			}

			// Check if the last message received time exceeds the timeout
			if time.Since(lastMessageReceivedTime) >= receivingMessageTimeout {
				toExit = true

				// Send a timeout error message
				internalusbcdc.USBCDCHandler.SendErrorMessage(internalusbcdc.ErrorCodeUSBCDCReceivingMessageTimeoutReached)

				// Stop the motor and center the servo
				stopAndCenter()
				break
			}

			// Check if a new message has arrived
			hasNewMessageArrived := internalusbcdc.USBCDCHandler.IsAvailableToRead()
			if !hasNewMessageArrived {
				time.Sleep(noMessageReceivedDelay)
				runtime.Gosched()
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
			case internalusbcdc.IncomingCategoryGetMaxMotorSpeedValue:
				if err := internalusbcdc.USBCDCHandler.SendMaxMotorSpeedValueMessage(internalescmotor.MaxSpeed); err != tinygoerrors.ErrorCodeNil {
					internalusbcdc.USBCDCHandler.SendErrorMessage(err)
				}
			case internalusbcdc.IncomingCategoryGetMaxServoAngleValue:
				if err := internalusbcdc.USBCDCHandler.SendMaxServoAngleValueMessage(internalservo.MaxAngle); err != tinygoerrors.ErrorCodeNil {
					internalusbcdc.USBCDCHandler.SendErrorMessage(err)
				}
			case internalusbcdc.IncomingCategoryMotorSpeedStop:
				if err := internalescmotor.ESCMotorHandler.Stop(); err != tinygoerrors.ErrorCodeNil {
					internalusbcdc.USBCDCHandler.SendErrorMessage(err)
				}
			case internalusbcdc.IncomingCategoryServoAngleCenter:
				if err := internalservo.ServoHandler.SetAngleToCenter(); err != tinygoerrors.ErrorCodeNil {
					internalusbcdc.USBCDCHandler.SendErrorMessage(err)
				}
			case internalusbcdc.IncomingCategoryServoAngleToLeft, internalusbcdc.IncomingCategoryServoAngleToRight:
				if err := internalservo.SetDirectionBasedOnReceivedMessage(
					internalusbcdc.USBCDCHandler,
					newMessage,
				); err != tinygoerrors.ErrorCodeNil {
					internalusbcdc.USBCDCHandler.SendErrorMessage(err)
				}
			case internalusbcdc.IncomingCategoryMotorSpeedForward, internalusbcdc.IncomingCategoryMotorSpeedBackward:
				if err := internalescmotor.SetSpeedBasedOnReceivedMessage(
					internalusbcdc.USBCDCHandler,
					newMessage,
				); err != tinygoerrors.ErrorCodeNil {
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
	}
}
