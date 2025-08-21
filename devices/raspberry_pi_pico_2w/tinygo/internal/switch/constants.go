package _switch

import (
	"time"

	"machine"

	internalpullup "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/pullup"
)

var (
	// DefaultInterval is the default interval for the switch ON signal.
	DefaultInterval = 10 * time.Millisecond

	// PullUpHandler is the handler for the pull-up for the switch ON signal.
	PullUpHandler internalpullup.Handler = internalpullup.NewDefaultHandler(machine.GPIO21)

	// SwitchHandler is the default switch handler that uses the pull-up handler.
	SwitchHandler, _ = NewDefaultHandler(
		PullUpHandler,
		DefaultInterval,
	)
)

func init() {
	// Call the setup function to initialize the pull-up
	SwitchHandler.Setup()
}
