package main

import (
	"fmt"
	"time"

	internalbno08x "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/bno08x"
	internalledonboard "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/led/onboard"
)

func main() {
	startTime := time.Now()
	for {
		// Check if the BNO08X needs to be reset
		if time.Since(startTime) >= internalbno08x.ResetBNO08XInterval {
			// if time.Since(startTime) >= 10*time.Second {
			// Reset BNO08X
			if err := internalbno08x.BNO08XHandler.Reset(); err != nil {
				fmt.Println(
					fmt.Errorf(
						"failed to initialize bno08x: %w",
						err,
					),
				)
			} else {
				startTime = time.Now()
			}
		}

		// Turn on the LED
		internalledonboard.OnBoardHandler.SetOn()

		// Update quaternion
		if err := internalbno08x.BNO08XHandler.Update(); err != nil {
			fmt.Println(fmt.Errorf("failed to update bno08x: %w", err))
		}

		// Turn off the LED
		internalledonboard.OnBoardHandler.SetOff()

		time.Sleep(100 * time.Millisecond)
	}
}
