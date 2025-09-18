package servo

import (
	internalusbcdc "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/usbcdc"
	tinygoerrors "github.com/ralvarezdev/tinygo-errors"
	tinygobuffers "github.com/ralvarezdev/tinygo-buffers"
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
func SetDirectionBasedOnReceivedMessage(handler internalusbcdc.Handler, message internalusbcdc.IncomingMessage) tinygoerrors.ErrorCode {
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
		// Send feedback message
		if handler != nil {
			handler.SendSetServoDirectionCenterMessage()
		}

		// Center the servo
		return ServoHandler.SetAngleToCenter()
	case internalusbcdc.IncomingCategoryServoDirectionToLeft:
		// Send feedback message
		if handler != nil {
			handler.SendSetServoDirectionToLeftMessage(servoDirectionAngle)
		}
		
		// Set the servo direction to left
		return ServoHandler.SafeSetAngleToLeft(servoDirectionAngle)
	case internalusbcdc.IncomingCategoryServoDirectionToRight:
		// Send feedback message
		if handler != nil {
			handler.SendSetServoDirectionToRightMessage(servoDirectionAngle)
		}

		// Set the servo direction to right
		return ServoHandler.SafeSetAngleToRight(servoDirectionAngle)
	default:
		return internalusbcdc.ErrorCodeUSBCDCUnknownIncomingCategory
	}
}
