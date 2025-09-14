package escmotor

import (
	"machine"

	tinygoescmotor "github.com/ralvarezdev/tinygo-escmotor"
	tinygotypes "github.com/ralvarezdev/tinygo-types"
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
func (e *DefaultHandler) SetSpeedBasedOnReceivedMessage(message internalusbcdc.IncomingMessage) tinygotypes.ErrorCode {

	// Check if the motor speed should be retrieved from the message
	var motorSpeed uint16
	if message.Category != internalusbcdc.IncomingCategoryMotorSpeedStop {
		// Get int16 speed from message content
		speed, err := message.GetContentAsUint16()
		if err != tinygotypes.ErrorCodeNil {
			return ErrorCodeESCMotorInvalidMotorSpeedValue
		}
		motorSpeed = speed
	}

	// Check the motor speed category
	switch message.Category {
	case internalusbcdc.IncomingCategoryMotorSpeedStop:
		return e.Stop()
	case internalusbcdc.IncomingCategoryMotorSpeedForward:
		return e.SetSpeedForward(motorSpeed)
	case internalusbcdc.IncomingCategoryMotorSpeedBackward:
		return e.SetSpeedBackward(motorSpeed)
	default:
		return ErrorCodeESCMotorUnknownMotorSpeedCategory
	}
}
