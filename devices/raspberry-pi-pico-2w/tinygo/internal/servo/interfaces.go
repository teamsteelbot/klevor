package servo

import (
	internalusbcdc "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/usbcdc"
)

type (
	// Handler is the interface to handle servo operations
	Handler interface {
		SetAngle(angle uint16) error
		GetAngle() uint16
		SetAngleRelativeToCenter(relativeAngle int16) error
		IsAngleCentered() bool
		SetAngleToCenter() error
		SetAngleToRight(angle uint16) error
		SetAngleToLeft(angle uint16) error
		SetDirectionToCenter() error
		SetDirectionToRight(angle uint16) error
		SetDirectionToLeft(angle uint16) error
		SetDirectionBasedOnReceivedMessage(message *internalusbcdc.IncomingMessage) error
	}
)
