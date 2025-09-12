package _switch

import (
	"time"

	"machine"

	internalpullup "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/pullup"
	tinygotypes "github.com/ralvarezdev/tinygo-types"
	"github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal"
)

var (
	// DefaultInterval is the default interval for the switch ON signal.
	DefaultInterval = 10 * time.Millisecond

	// PullUpHandler is the handler for the pull-up for the switch ON signal.
	PullUpHandler internalpullup.Handler = internalpullup.NewDefaultHandler(machine.GPIO27)

	// SwitchHandler is the default switch handler that uses the pull-up handler.
	SwitchHandler Handler

	// failedToInitializeSwitchMessage is the message printed when switch initialization fails
	failedToInitializeSwitchMessage = []byte("Failed to initialize switch handler:")
)

func init() {
	switchHandler, err := NewDefaultHandler(
		PullUpHandler,
		DefaultInterval,
	)
	if err != tinygotypes.ErrorCodeNil {
		internal.Logger.ErrorMessageWithErrorCode(failedToInitializeSwitchMessage, err)
	}
	SwitchHandler = switchHandler

	// Call the setup function to initialize the pull-up
	SwitchHandler.Setup()
}
