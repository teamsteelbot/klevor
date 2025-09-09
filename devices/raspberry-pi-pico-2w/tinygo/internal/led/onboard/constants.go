package onboard

import (
	"errors"

	internalcyw43439 "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/cyw43439"
	internalled "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/led"
	tinygotypes "github.com/ralvarezdev/tinygo-types"
)

var (
	// OnBoardHandler is the default handler for the onboard LED of the Raspberry Pi Pico 2W.
	OnBoardHandler internalled.Handler
)

func init() {
	onBoardHandler, err := NewDefaultHandler(internalcyw43439.Device)
	if err != tinygotypes.ErrorCodeNil {
		panic(errors.New("failed to initialize on board led handler"))
	}
	OnBoardHandler = onBoardHandler
}
