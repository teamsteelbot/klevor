package _switch

import (
	"github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/pulldown"
)

type (
	// Handler is the interface to manage the switch state.
	Handler interface {
		pulldown.Handler
		Wait(onEvent func()) error
	}
)
