package servo

import (
	internalusbcdc "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/usbcdc"
	tinygotypes "github.com/ralvarezdev/tinygo-types"
)

type (
	// Handler is the interface to handle servo operations
	Handler interface {
		SetAngle(angle uint16) tinygotypes.ErrorCode
		GetAngle() uint16
		SetAngleRelativeToCenter(relativeAngle int16) tinygotypes.ErrorCode
		IsAngleCentered() bool
		SetAngleToCenter() tinygotypes.ErrorCode
		SetAngleToRight(angle uint16) tinygotypes.ErrorCode
		SetAngleToLeft(angle uint16) tinygotypes.ErrorCode
		SetDirectionToCenter() tinygotypes.ErrorCode
		SetDirectionToRight(angle uint16) tinygotypes.ErrorCode
		SetDirectionToLeft(angle uint16) tinygotypes.ErrorCode
		SetDirectionBasedOnReceivedMessage(message *internalusbcdc.IncomingMessage) tinygotypes.ErrorCode
	}
)
