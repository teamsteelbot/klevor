package escmotor

import (
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
		// Stop the motor
		if err := ESCMotorHandler.Stop(); err != tinygoerrors.ErrorCodeNil {
			return err
		}
		// Send feedback message
		return handler.SendSetMotorSpeedStopMessage()
	case internalusbcdc.IncomingCategoryMotorSpeedForward:
		// Set the motor speed
		if err := ESCMotorHandler.SafeSetSpeedForward(motorSpeed); err != tinygoerrors.ErrorCodeNil {
			return err
		}
		// Send feedback message
		return handler.SendSetMotorSpeedForwardMessage(motorSpeed)
	case internalusbcdc.IncomingCategoryMotorSpeedBackward:
		// Set the motor speed
		if err := ESCMotorHandler.SafeSetSpeedBackward(motorSpeed); err != tinygoerrors.ErrorCodeNil {
			return err
		}
		// Send feedback message
		return handler.SendSetMotorSpeedBackwardMessage(motorSpeed)
	default:
		return internalusbcdc.ErrorCodeUSBCDCUnknownIncomingCategory
	}
}
