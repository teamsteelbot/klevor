package enabler

import (
	"github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/pulldown"
)

type (
	// Handler is the interface to handle pull-down resistor operations for enabling features
	Handler interface {
		pulldown.Handler
		IsEnabled() bool
		IsDisabled() bool
	}
)
