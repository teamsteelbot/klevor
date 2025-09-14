package main

import (
	"fmt"
	"os"
	"sync"
	"time"

	"github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal"
	internalbno08x "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/bno08x"
	internalescmotor "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/escmotor"
	internalledonboard "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/led/onboard"
	internalservo "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/servo"
	internalswitch "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/switch"
	internalusbcdc "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/usbcdc"
	tinygobuffers "github.com/ralvarezdev/tinygo-buffers"
	tinygotypes "github.com/ralvarezdev/tinygo-types"
)

const (
	// receivingMessageTimeout defines the maximum time to wait for receiving messages.
	receivingMessageTimeout = 5 * time.Second
)

var (
	// failedToSendErrorMessage is the message printed when sending an error message fails.
	failedToSendErrorMessage = []byte("Failed to send error message via USB-CDC:")

	// failedToWaitForSwitchPressMessage is the message printed when waiting for switch press fails.
	failedToWaitForSwitchPressMessage = []byte("Failed to wait for switch press:")

	// switchOnEvent is called when the switch is pressed to initialize communication and provide visual feedback.
	switchOnEvent func() tinygotypes.ErrorCode

	// lastMessageReceivedTime holds the timestamp of the last received message.
	lastMessageReceivedTime time.Time

	// hasNewMessageArrived indicates if a new message has arrived.
	hasNewMessageArrived bool

	// newMessage is the newly received message.
	newMessage internalusbcdc.IncomingMessage
)

// sendErrorMessage sends an error message via USB CDC if there is an error to be sent.
//
// Parameters:
//
// err: The error to be sent.
func sendErrorMessage(err tinygotypes.ErrorCode) {
	err = internalusbcdc.USBCDCHandler.SendErrorMessage(err)
	if err != tinygotypes.ErrorCodeNil {
		internal.Logger.ErrorMessageWithErrorCode(failedToSendErrorMessage, err, true)
		os.Exit(1)
	}
}

// sendErrorMessageOnError sends an error message via USB CDC if there is an error to be sent.
//
// Parameters:
//
// fn: A function that returns a tinygotypes.ErrorCode to be checked.
func sendErrorMessageOnError(fn func() tinygotypes.ErrorCode) {
	if err := fn(); err != tinygotypes.ErrorCodeNil {
		sendErrorMessage(err)
	}
}

// stopAndCenter stops the ESC motor and centers the servo concurrently.
func stopAndCenter() {
	var wg sync.WaitGroup

	// ESC motor stop
	wg.Add(1)
	go func() {
		defer wg.Done()
		sendErrorMessageOnError(internalescmotor.ESCMotorHandler.Stop)
	}()

	// Servo center
	wg.Add(1)
	go func() {
		defer wg.Done()
		sendErrorMessageOnError(internalservo.ServoHandler.SetDirectionToCenter)
	}()

	wg.Wait()
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
		if err := internalswitch.SwitchHandler.Wait(switchOnEvent); err != tinygotypes.ErrorCodeNil {
			internal.Logger.ErrorMessageWithErrorCode(failedToWaitForSwitchPressMessage, err, true)
			os.Exit(1)
		}

		// Last time the BNO08X was updated
		lastBNO08XUpdateTime := time.Now()

		// Set the exit condition to False
		toExit := false
		for !toExit {
			// Check if the last message received time exceeds the timeout
			if time.Since(lastMessageReceivedTime) >= receivingMessageTimeout {
				toExit = true

				// Stop the motor and center the servo
				stopAndCenter()
				break
			}

			// Create a wait group to handle concurrent tasks
			var wg sync.WaitGroup

			// Check if the BNO08X needs to be updated
			if time.Since(lastBNO08XUpdateTime) >= internalbno08x.Interval {
				internalbno08x.UARTRVC.Update()
				lastBNO08XUpdateTime = time.Now()

				wg.Add(1)
				go func() {
					defer wg.Done()

					// Update the BNO08X sensor data
					sendErrorMessageOnError(
						internalbno08x.UARTRVC.Update,
					)

					// Get the Euler degrees from the BNO08X sensor
					eulerDegrees := internalbno08x.UARTRVC.GetEulerDegrees()

					// Send the Euler degrees messages via USB CDC
					sendErrorMessageOnError(
						func() tinygotypes.ErrorCode {
							return internalusbcdc.USBCDCHandler.SendBNO08XEulerDegreesMessages(eulerDegrees)
						},
					)
				}()
			}

			// Receive USB CDC messages
			wg.Add(1)
			go func() {
				defer wg.Done()

				// Read a message with a timeout
				hasNewMessageArrived = false
				message, err := internalusbcdc.USBCDCHandler.ReadMessage(internalbno08x.Interval)
				if err != tinygotypes.ErrorCodeNil {
					sendErrorMessage(err)
				}
				newMessage = message
				hasNewMessageArrived = true
			}()

			// Wait for both to finish
			wg.Wait()

			// Check if a new message has arrived
			if !hasNewMessageArrived {
				continue
			}

			// Reset the last message received time if messages are received
			lastMessageReceivedTime = time.Now()

			// Handle specific message categories
			switch newMessage.Category {
			case internalusbcdc.IncomingCategoryGetMaxMotorSpeedValue:
				sendErrorMessageOnError(
					func() tinygotypes.ErrorCode {
						return internalusbcdc.USBCDCHandler.SendMaxMotorSpeedValueMessage(internalescmotor.MaxSpeed)
					},
				)
			case internalusbcdc.IncomingCategoryGetMaxServoDirectionValue:
				sendErrorMessageOnError(
					func() tinygotypes.ErrorCode {
						return internalusbcdc.USBCDCHandler.SendMaxServoDirectionValueMessage(internalservo.MaxDirection)
					},
				)
			case internalusbcdc.IncomingCategoryMotorSpeedStop:
				sendErrorMessageOnError(internalescmotor.ESCMotorHandler.Stop)
			case internalusbcdc.IncomingCategoryServoDirectionCenter:
				sendErrorMessageOnError(internalservo.ServoHandler.SetDirectionToCenter)
			case internalusbcdc.IncomingCategoryServoDirectionToLeft, internalusbcdc.IncomingCategoryServoDirectionToRight:
				sendErrorMessageOnError(
					func() tinygotypes.ErrorCode {
						return internalservo.SetDirectionBasedOnReceivedMessage(newMessage)
					},
				)
			case internalusbcdc.IncomingCategoryMotorSpeedForward, internalusbcdc.IncomingCategoryMotorSpeedBackward:
				sendErrorMessageOnError(
					func() tinygotypes.ErrorCode {
						return internalescmotor.SetSpeedBasedOnReceivedMessage(newMessage)
					},
				)
			case internalusbcdc.IncomingCategoryStatus:
				// Get the first byte of the message content
				if len(newMessage.Data) < 1 {
					sendErrorMessage(internalusbcdc.ErrorCodeUSBCDCInvalidMessageDataLength)
					continue
				}

				// Parse the status from the first byte
				statusUint8, err := tinygobuffers.BytesToUint8(newMessage.Data[0])
				if err != tinygotypes.ErrorCodeNil {
					sendErrorMessage(err)
					continue
				}

				// Get the status from the message content
				status, err := internalusbcdc.IncomingStatusFromUint8(statusUint8)
				if err != nil {
					sendErrorMessage(err)
					continue
				}

				switch status {
				case internalusbcdc.IncomingStatusHeartbeat:
					break
				case internalusbcdc.IncomingStatusOK:
					sendErrorMessage(internalusbcdc.ErrorCodeUSBCDCReceivedUnexpectedConfirmationMessage)
					continue
				case internalusbcdc.IncomingStatusStop:
					// Set the exit condition to True
					toExit = true

					// Stop the motor and center the servo
					stopAndCenter()

					// Send a confirmation message to the serial communication
					sendErrorMessageOnError(
						func() tinygotypes.ErrorCode {
							return internalusbcdc.USBCDCHandler.SendConfirmationMessage()
						},
					)
				}
			}
		}

		// Break the loop if the exit flag is set
		if toExit {
			break
		}

	}
}
