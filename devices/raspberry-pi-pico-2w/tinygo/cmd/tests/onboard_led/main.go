package main

import (
	"time"

	internalledonboard "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/led/onboard"
)

func main() {
	for {
		// Turn LED on
		internalledonboard.OnBoardHandler.SetOn()
		println("LED ON")
		time.Sleep(500 * time.Millisecond)

		// Turn LED off
		internalledonboard.OnBoardHandler.SetOff()
		println("LED OFF")
		time.Sleep(500 * time.Millisecond)
	}
}
