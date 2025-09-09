package led

import (
	"time"

	tinygotypes "github.com/ralvarezdev/tinygo-types"
)

type (
	// Handler is the interface to manage the onboard LED of the Raspberry Pi Pico 2W or any other LED.
	Handler interface {
		Setup()
		SetOn()
		IsOn() bool
		SetOff()
		IsOff() bool
		Toggle()
		Blink(times int, delay time.Duration) tinygotypes.ErrorCode
	}
)
