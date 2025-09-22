package escmotor

import (
	"math"

	internalusbcdc "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/usbcdc"
	tinygobuffers "github.com/ralvarezdev/tinygo-buffers"
	tinygoerrors "github.com/ralvarezdev/tinygo-errors"
)

// SetSpeedBasedOnReceivedMessage sets the motor speed based on the received message
//
// Parameters:
//
// message: The incoming message containing the motor speed command
// handler: The USB CDC handler to send error messages if needed
//
// Returns:
//
// An error if the motor speed could not be set, otherwise nil
func SetSpeedBasedOnReceivedMessage(
	handler internalusbcdc.Handler,
	message internalusbcdc.IncomingMessage,
) tinygoerrors.ErrorCode {
	// Check if the USB-CDC handler is nil
	if handler == nil {
		return internalusbcdc.ErrorCodeUSBCDCNilHandler
	}

	// Check if the message category is valid
	if message.Category != internalusbcdc.IncomingCategoryMotorSpeedStop &&
		message.Category != internalusbcdc.IncomingCategoryMotorSpeedForward &&
		message.Category != internalusbcdc.IncomingCategoryMotorSpeedBackward {
		return internalusbcdc.ErrorCodeUSBCDCUnknownIncomingCategory
	}

	// Check if the motor speed should be retrieved from the message
	var motorSpeedPercentage float64
	if message.Category != internalusbcdc.IncomingCategoryMotorSpeedStop {
		// Get speed percentage from message content
		speedPercentage, err := tinygobuffers.BytesToFloat64(message.Data)
		if err != tinygoerrors.ErrorCodeNil {
			return err
		}
		motorSpeedPercentage = math.Abs(speedPercentage)
	}

	// Send start feedback message
	if err := handler.SendMotorSpeedStartMessage(); err != tinygoerrors.ErrorCodeNil {
		return err
	}

	// Check the motor speed category
	switch message.Category {
	case internalusbcdc.IncomingCategoryMotorSpeedStop:
		// Stop the motor
		if err := ESCMotorHandler.Stop(); err != tinygoerrors.ErrorCodeNil {
			return err
		}
	case internalusbcdc.IncomingCategoryMotorSpeedForward:
		// Set the motor speed
		if err := ESCMotorHandler.SetSpeedForward(motorSpeedPercentage); err != tinygoerrors.ErrorCodeNil {
			return err
		}
	case internalusbcdc.IncomingCategoryMotorSpeedBackward:
		// Set the motor speed
		if err := ESCMotorHandler.SetSpeedBackward(motorSpeedPercentage); err != tinygoerrors.ErrorCodeNil {
			return err
		}
	}

	// Send feedback message
	return handler.SendMotorSpeedEndMessage()
}
