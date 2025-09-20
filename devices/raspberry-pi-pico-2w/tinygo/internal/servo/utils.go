package servo

import (
	internalusbcdc "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/usbcdc"
	tinygobuffers "github.com/ralvarezdev/tinygo-buffers"
	tinygoerrors "github.com/ralvarezdev/tinygo-errors"
)

// SetAngleBasedOnReceivedMessage sets the servo angle based on the received message
//
// Parameters:
//
// handler: The USB CDC handler to send error messages if needed
// message: The incoming message containing the servo angle command
//
// Returns:
//
// An error if the servo angle could not be set
func SetAngleBasedOnReceivedMessage(
	handler internalusbcdc.Handler,
	message internalusbcdc.IncomingMessage,
) tinygoerrors.ErrorCode {
	// Check if the handler is nil
	if handler == nil {
		return internalusbcdc.ErrorCodeUSBCDCNilHandler
	}

	// Check if the message category is valid
	if message.Category != internalusbcdc.IncomingCategoryServoAngleCenter &&
		message.Category != internalusbcdc.IncomingCategoryServoAngleToLeft &&
		message.Category != internalusbcdc.IncomingCategoryServoAngleToRight {
		return internalusbcdc.ErrorCodeUSBCDCUnknownIncomingCategory
	}

	// Check if the servo angle should be retrieved from the message
	var servoDirectionAngle uint16
	if message.Category != internalusbcdc.IncomingCategoryServoAngleCenter {
		// Get uint16 angle from message content
		angle, err := tinygobuffers.BytesToUint16(message.Data)
		if err != tinygoerrors.ErrorCodeNil {
			return err
		}
		servoDirectionAngle = angle
	}

	// Send start feedback message
	if err := handler.SendServoAngleStartMessage(); err != tinygoerrors.ErrorCodeNil {
		return err
	}

	// Check the servo angle category
	switch message.Category {
	case internalusbcdc.IncomingCategoryServoAngleCenter:
		// Center the servo
		if err := ServoHandler.SetAngleToCenter(); err != tinygoerrors.ErrorCodeNil {
			return err
		}
	case internalusbcdc.IncomingCategoryServoAngleToLeft:
		// Set the servo angle to left
		if err := ServoHandler.SafeSetAngleToLeft(servoDirectionAngle); err != tinygoerrors.ErrorCodeNil {
			return err
		}
	case internalusbcdc.IncomingCategoryServoAngleToRight:
		// Set the servo angle to right
		if err := ServoHandler.SafeSetAngleToRight(servoDirectionAngle); err != tinygoerrors.ErrorCodeNil {
			return err
		}
	}

	// Send end feedback message
	return handler.SendServoAngleEndMessage()
}
