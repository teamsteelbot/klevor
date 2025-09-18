package servo

import (
	internalusbcdc "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/usbcdc"
	tinygobuffers "github.com/ralvarezdev/tinygo-buffers"
	tinygoerrors "github.com/ralvarezdev/tinygo-errors"
)

// SetDirectionBasedOnReceivedMessage sets the servo direction based on the received message
//
// Parameters:
//
// handler: The USB CDC handler to send error messages if needed
// message: The incoming message containing the servo direction command
//
// Returns:
//
// An error if the servo direction could not be set
func SetDirectionBasedOnReceivedMessage(
	handler internalusbcdc.Handler,
	message internalusbcdc.IncomingMessage,
) tinygoerrors.ErrorCode {
	// Check if the handler is nil
	if handler == nil {
		return internalusbcdc.ErrorCodeUSBCDCNilHandler
	}

	// Check if the servo angle should be retrieved from the message
	var servoDirectionAngle uint16
	if message.Category != internalusbcdc.IncomingCategoryServoDirectionCenter {
		// Get uint16 angle from message content
		angle, err := tinygobuffers.BytesToUint16(message.Data)
		if err != tinygoerrors.ErrorCodeNil {
			return err
		}
		servoDirectionAngle = angle
	}

	// Check the servo angle category
	switch message.Category {
	case internalusbcdc.IncomingCategoryServoDirectionCenter:
		// Center the servo
		if err := ServoHandler.SetAngleToCenter(); err != tinygoerrors.ErrorCodeNil {
			return err
		}
		// Send feedback message
		return handler.SendSetServoDirectionCenterMessage()
	case internalusbcdc.IncomingCategoryServoDirectionToLeft:
		// Set the servo direction to left
		if err := ServoHandler.SafeSetAngleToLeft(servoDirectionAngle); err != tinygoerrors.ErrorCodeNil {
			return err
		}
		// Send feedback message
		return handler.SendSetServoDirectionToLeftMessage()
	case internalusbcdc.IncomingCategoryServoDirectionToRight:
		// Set the servo direction to right
		if err := ServoHandler.SafeSetAngleToRight(servoDirectionAngle); err != tinygoerrors.ErrorCodeNil {
			return err
		}
		// Send feedback message
		return handler.SendSetServoDirectionToRightMessage()
	default:
		return internalusbcdc.ErrorCodeUSBCDCUnknownIncomingCategory
	}
}
