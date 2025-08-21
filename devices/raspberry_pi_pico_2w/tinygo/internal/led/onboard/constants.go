package onboard

import (
	internalcyw43439 "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/cyw43439"
)

var (
	// OnBoardHandler is the default handler for the onboard LED of the Raspberry Pi Pico 2W.
	OnBoardHandler, _ = NewDefaultHandler(internalcyw43439.Device)
)
