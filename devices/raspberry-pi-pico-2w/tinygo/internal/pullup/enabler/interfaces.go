package enabler

import (
	internalpullup "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/pullup"
)

type (
	// Handler is the interface to handle pull-up resistor operations for enabling features
	Handler interface {
		internalpullup.Handler
		IsEnabled() bool
		IsDisabled() bool
	}
)
