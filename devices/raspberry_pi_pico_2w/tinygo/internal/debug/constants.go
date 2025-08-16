package debug

import (
	"machine"

	"github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/pulldown"
)

var (
	// PullDownHandler is the handler for the pull-down for the debug mode.
	PullDownHandler pulldown.Handler = pulldown.NewDefaultHandler(machine.GPIO27)

	// DebugHandler is the default debug handler that uses the pull-down handler.
	DebugHandler, _ = NewDefaultHandler(
		PullDownHandler,
	)
)
