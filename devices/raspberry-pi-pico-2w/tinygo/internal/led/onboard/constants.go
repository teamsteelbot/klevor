package onboard

import (
	"fmt"

	internalcyw43439 "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/cyw43439"
	internalled "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/led"
)

var (
	// OnBoardHandler is the default handler for the onboard LED of the Raspberry Pi Pico 2W.
	OnBoardHandler internalled.Handler
)

func init() {
	onBoardHandler, err := NewDefaultHandler(internalcyw43439.Device)
	if err != nil {
		panic(fmt.Errorf("failed to initialize on board led handler: %w", err))
	}
	OnBoardHandler = onBoardHandler
}
