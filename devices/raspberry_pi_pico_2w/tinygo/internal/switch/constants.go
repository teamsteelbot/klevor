package _switch

import (
	"time"

	"machine"

	"github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/pulldown"
)

var (
	// DefaultInterval is the default interval for the switch ON signal.
	DefaultInterval = 10 * time.Millisecond

	// PullDownHandler is the handler for the pull-down for the switch ON signal.
	PullDownHandler pulldown.Handler = pulldown.NewDefaultHandler(machine.GPIO21)

	// SwitchHandler is the default switch handler that uses the pull-down handler.
	SwitchHandler, _ Handler = NewDefaultHandler(
		PullDownHandler,
		DefaultInterval,
	)
)
