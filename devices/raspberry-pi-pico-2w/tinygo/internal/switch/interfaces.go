package _switch

import (
	internalpullup "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/pullup"
)

type (
	// Handler is the interface to manage the switch state.
	Handler interface {
		internalpullup.Handler
		Wait(onEvent func() error) error
	}
)
