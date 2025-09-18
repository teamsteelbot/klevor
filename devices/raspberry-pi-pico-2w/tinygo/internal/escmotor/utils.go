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
// handler: The USB CDC handler to send error messages if needed
//
// Returns:
//
// An error if the motor speed could not be set, otherwise nil
func SetSpeedBasedOnReceivedMessage(handler internalusbcdc.Handler, message internalusbcdc.IncomingMessage) tinygoerrors.ErrorCode {
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
		// Send feedback message
		if handler != nil {
			handler.SendSetMotorSpeedStopMessage()
		}

		// Stop the motor
		return ESCMotorHandler.Stop()
	case internalusbcdc.IncomingCategoryMotorSpeedForward:
		// Send feedback message
		if handler != nil {
			handler.SendSetMotorSpeedForwardMessage(motorSpeed)
		}

		// Set the motor speed
		return ESCMotorHandler.SafeSetSpeedForward(motorSpeed)
	case internalusbcdc.IncomingCategoryMotorSpeedBackward:
		// Send feedback message
		if handler != nil {
			handler.SendSetMotorSpeedBackwardMessage(motorSpeed)
		}

		// Set the motor speed
		return ESCMotorHandler.SafeSetSpeedBackward(motorSpeed)
	default:
		return internalusbcdc.ErrorCodeUSBCDCUnknownIncomingCategory
	}
}
