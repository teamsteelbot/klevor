package _switch

import (
	internalpullup "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/pullup"
	tinygotypes "github.com/ralvarezdev/tinygo-types"
)

type (
	// Handler is the interface to manage the switch state.
	Handler interface {
		internalpullup.Handler
		Wait(onEvent func() tinygotypes.ErrorCode) tinygotypes.ErrorCode
	}
)
