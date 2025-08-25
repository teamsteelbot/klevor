package main

import (
	"fmt"
	"time"

	internalbno08x "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/bno08x"
)

func main() {
	for {
		// Update quaternion
		if err := internalbno08x.BNO08XHandler.Update(); err != nil {
			fmt.Println(fmt.Errorf("failed to update bno08x: %w", err))
		}

		fmt.Printf("\n***** Updated *****\n")

		// Print the current orientation
		fmt.Printf(
			"Yaw: %.2f°, Pitch: %.2f°, Roll: %.2f°, Turns: %d\n",
			internalbno08x.BNO08XHandler.GetYawDegrees(),
			internalbno08x.BNO08XHandler.GetPitchDegrees(),
			internalbno08x.BNO08XHandler.GetRollDegrees(),
			internalbno08x.BNO08XHandler.GetAccumulatedYaw90DegreesTurns(),
		)
		time.Sleep(50 * time.Millisecond)
	}
}
