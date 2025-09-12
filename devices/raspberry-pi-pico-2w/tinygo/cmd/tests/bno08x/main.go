package main

import (
	"time"

	"github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal"
	internalbno08x "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/bno08x"
	ralvarezdevbno08x "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/bno08x/test"
	//ralvarezdevbno08x "github.com/ralvarezdev/tinygo-bno08x"
	//tinygotypes "github.com/ralvarezdev/tinygo-types"
)

const (
	// IntervalDuration is the duration of the main loop interval
	IntervalDuration = 100 * time.Millisecond
)

func main() {
	// Wait 5 seconds before starting the test
	time.Sleep(5 * time.Second)

	for {
		// Update quaternion
		internalbno08x.BNO08XSimpleService.Update()

		// Print quaternion
		q := internalbno08x.BNO08XSimpleService.GetQuaternion()
		x := q[ralvarezdevbno08x.QuaternionXIndex]
		y := q[ralvarezdevbno08x.QuaternionYIndex]
		z := q[ralvarezdevbno08x.QuaternionZIndex]
		w := q[ralvarezdevbno08x.QuaternionWIndex]

		// Get the formatted time string
		currentTime := time.Now()
		timeString := currentTime.Format("15:04:05.000")
		println("[", timeString, "] Quaternion: x =", x, "y =", y, "z =", z, "w =", w)

		// Sleep for the interval duration
		time.Sleep(IntervalDuration)

		// Print memory stats
		internal.PrintMemory()
	}
}
