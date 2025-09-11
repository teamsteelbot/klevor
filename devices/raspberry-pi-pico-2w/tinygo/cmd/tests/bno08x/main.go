package main

import (
	"time"

	internalbno08x "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/bno08x"
	ralvarezdevbno08x "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/bno08x/test"
	//ralvarezdevbno08x "github.com/ralvarezdev/tinygo-bno08x"
	tinygotypes "github.com/ralvarezdev/tinygo-types"
)

const (
	// IntervalDuration is the duration of the main loop interval
	IntervalDuration = 100 * time.Millisecond
)

func main() {
	startTime := time.Now()
	for {
		// Check if the BNO08X needs to be reset
		if time.Since(startTime) >= internalbno08x.ResetBNO08XInterval {
			// Reset BNO08X
			if err := internalbno08x.BNO08XSimpleService.Reset(); err != tinygotypes.ErrorCodeNil {
				return
			} else {
				startTime = time.Now()
			}
		}

		// Update quaternion
		internalbno08x.BNO08XSimpleService.Update()

		// Print quaternion
		q := internalbno08x.BNO08XSimpleService.GetQuaternion()
		x := q[ralvarezdevbno08x.QuaternionXIndex]
		y := q[ralvarezdevbno08x.QuaternionYIndex]
		z := q[ralvarezdevbno08x.QuaternionZIndex]
		w := q[ralvarezdevbno08x.QuaternionWIndex]
		println("Quaternion: W:", w, " X:", x, " Y:", y, " Z:", z)

		// Sleep for the interval duration
		time.Sleep(IntervalDuration)
	}
}
