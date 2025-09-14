package servo

import (
	internalusbcdc "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/usbcdc"
	tinygotypes "github.com/ralvarezdev/tinygo-types"
	tinygobuffers "github.com/ralvarezdev/tinygo-buffers"
)

// SetDirectionBasedOnReceivedMessage sets the servo direction based on the received message
//
// Parameters:
//
// message: The incoming message containing the servo direction command
//
// Returns:
//
// An error if the servo direction could not be set
func SetDirectionBasedOnReceivedMessage(message internalusbcdc.IncomingMessage) tinygotypes.ErrorCode {
	// Check if the servo angle should be retrieved from the message
	var servoDirectionAngle uint16
	if message.Category != internalusbcdc.IncomingCategoryServoDirectionCenter {
		// Get uint16 angle from message content
		angle, err := tinygobuffers.BytesToUint16(message.Data)
		if err != tinygotypes.ErrorCodeNil {
			return err
		}
		servoDirectionAngle = angle
	}

	// Check the servo angle category
	switch message.Category {
	case internalusbcdc.IncomingCategoryServoDirectionCenter:
		return ServoHandler.SetDirectionToCenter()
	case internalusbcdc.IncomingCategoryServoDirectionToLeft:
		return ServoHandler.SetDirectionToLeft(servoDirectionAngle)
	case internalusbcdc.IncomingCategoryServoDirectionToRight:
		return ServoHandler.SetDirectionToRight(servoDirectionAngle)
	default:
		return internalusbcdc.ErrorCodeUSBCDCUnknownIncomingCategory
	}
}
