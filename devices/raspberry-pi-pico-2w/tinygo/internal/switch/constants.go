package _switch

import (
	"errors"
	"time"

	"machine"

	internalpullup "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/pullup"
	tinygotypes "github.com/ralvarezdev/tinygo-types"
)

var (
	// DefaultInterval is the default interval for the switch ON signal.
	DefaultInterval = 10 * time.Millisecond

	// PullUpHandler is the handler for the pull-up for the switch ON signal.
	PullUpHandler internalpullup.Handler = internalpullup.NewDefaultHandler(machine.GPIO27)

	// SwitchHandler is the default switch handler that uses the pull-up handler.
	SwitchHandler Handler
)

func init() {
	switchHandler, err := NewDefaultHandler(
		PullUpHandler,
		DefaultInterval,
	)
	if err != tinygotypes.ErrorCodeNil {
		panic(errors.New("failed to initialize switch handler"))
	}
	SwitchHandler = switchHandler

	// Call the setup function to initialize the pull-up
	SwitchHandler.Setup()
}
