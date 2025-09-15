package escmotor

import (
	internalusbcdc "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/usbcdc"
	tinygoerrors "github.com/ralvarezdev/tinygo-errors"
	tinygobuffers "github.com/ralvarezdev/tinygo-buffers"
)


// SetSpeedBasedOnReceivedMessage sets the motor speed based on the received message
//
// Parameters:
//
// message: The incoming message containing the motor speed command
//
// Returns:
//
// An error if the motor speed could not be set, otherwise nil
func SetSpeedBasedOnReceivedMessage(message internalusbcdc.IncomingMessage) tinygoerrors.ErrorCode {
	// Check if the motor speed should be retrieved from the message
	var motorSpeed uint16
	if message.Category != internalusbcdc.IncomingCategoryMotorSpeedStop {
		// Get int16 speed from message content
		speed, err := tinygobuffers.BytesToUint16(message.Data)
		if err != tinygoerrors.ErrorCodeNil {
			return err
		}
		motorSpeed = speed
	}

	// Check the motor speed category
	switch message.Category {
	case internalusbcdc.IncomingCategoryMotorSpeedStop:
		return ESCMotorHandler.Stop()
	case internalusbcdc.IncomingCategoryMotorSpeedForward:
		return ESCMotorHandler.SetSpeedForward(motorSpeed)
	case internalusbcdc.IncomingCategoryMotorSpeedBackward:
		return ESCMotorHandler.SetSpeedBackward(motorSpeed)
	default:
		return internalusbcdc.ErrorCodeUSBCDCUnknownIncomingCategory
	}
}
