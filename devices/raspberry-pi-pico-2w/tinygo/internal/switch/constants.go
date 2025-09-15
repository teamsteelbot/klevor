package _switch

import (
	"os"
	"time"

	"machine"

	"github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal"
	tinygopullup "github.com/ralvarezdev/tinygo-pullup"
	tinygoerrors "github.com/ralvarezdev/tinygo-errors"
)

var (
	// DefaultInterval is the default interval for the switch ON signal.
	DefaultInterval = 10 * time.Millisecond

	// PullUpHandler is the handler for the pull-up for the switch ON signal.
	PullUpHandler = tinygopullup.NewDefaultHandler(machine.GPIO27)

	// SwitchHandler is the default switch handler that uses the pull-up handler.
	SwitchHandler Handler

	// failedToInitializeSwitchMessage is the message printed when switch initialization fails
	failedToInitializeSwitchMessage = []byte("Failed to initialize Switch Handler:")
)

func init() {
	switchHandler, err := NewDefaultHandler(
		PullUpHandler,
		DefaultInterval,
	)
	if err != tinygoerrors.ErrorCodeNil {
		internal.Logger.ErrorMessageWithErrorCode(failedToInitializeSwitchMessage, err, true)
		os.Exit(1)
	}
	SwitchHandler = switchHandler

	// Call the setup function to initialize the pull-up
	SwitchHandler.Setup()
}
