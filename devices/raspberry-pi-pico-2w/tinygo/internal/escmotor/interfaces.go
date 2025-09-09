package escmotor

import (
	tinygotypes "github.com/ralvarezdev/tinygo-types"
	internalusbcdc "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/usbcdc"
)

type (
	// Handler is the interface to handle ESC (Electronic Speed Controller) motor operations
	Handler interface {
		GetSpeed() int16
		SetSpeed(speed uint16, isForward bool) tinygotypes.ErrorCode
		Stop() tinygotypes.ErrorCode
		SetSpeedForward(speed uint16) tinygotypes.ErrorCode
		SetSpeedBackward(speed uint16) tinygotypes.ErrorCode
		SetSpeedBasedOnReceivedMessage(message *internalusbcdc.IncomingMessage) tinygotypes.ErrorCode
	}
)
