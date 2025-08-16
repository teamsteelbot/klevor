package debug

import (
	"machine"

	pulldownenabler "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/pulldown/enabler"
)

var (
	// Handler is the handler for the pull-down for the debug mode.
	Handler = pulldownenabler.NewDefaultHandlerFromPin(machine.GPIO10)
)
