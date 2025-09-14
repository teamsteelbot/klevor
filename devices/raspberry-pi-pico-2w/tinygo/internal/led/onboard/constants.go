package onboard

import (
	"os"

	"github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal"
	internalcyw43439 "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/cyw43439"
	internalled "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/led"
	tinygotypes "github.com/ralvarezdev/tinygo-types"
)

var (
	// OnBoardHandler is the default handler for the onboard LED of the Raspberry Pi Pico 2W.
	OnBoardHandler internalled.Handler

	// failedToInitializeOnBoardMessage is the message printed when onboard LED initialization fails
	failedToInitializeOnBoardMessage = []byte("Failed to initialize on board LED Handler:")
)

func init() {
	onBoardHandler, err := NewDefaultHandler(internalcyw43439.Device)
	if err != tinygotypes.ErrorCodeNil {
		internal.Logger.ErrorMessageWithErrorCode(failedToInitializeOnBoardMessage, err, true)
		os.Exit(1)
	}
	OnBoardHandler = onBoardHandler
}
