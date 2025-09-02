package escmotor

import (
	internalusbcdc "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/usbcdc"
)

type (
	// Handler is the interface to handle ESC (Electronic Speed Controller) motor operations
	Handler interface {
		GetSpeed() int16
		SetSpeed(speed uint16, isForward bool) error
		Stop() error
		SetSpeedForward(speed uint16) error
		SetSpeedBackward(speed uint16) error
		SetSpeedBasedOnReceivedMessage(message *internalusbcdc.IncomingMessage) error
	}
)
