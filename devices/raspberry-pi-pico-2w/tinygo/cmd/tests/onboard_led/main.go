package main

import (
	"time"

	internalledonboard "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/led/onboard"
)

const (
	// IntervalDuration is the duration of the LED on/off interval
	IntervalDuration = 500 * time.Millisecond
)

func main() {
	for {
		// Turn LED on
		internalledonboard.OnBoardHandler.SetOn()
		time.Sleep(IntervalDuration)

		// Turn LED off
		internalledonboard.OnBoardHandler.SetOff()
		time.Sleep(IntervalDuration)
	}
}
