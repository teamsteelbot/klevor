package main

import (
	"time"

	"github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal"
	internalbno08x "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/bno08x"
	ralvarezdevbno08x "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/bno08x/test"
	//ralvarezdevbno08x "github.com/ralvarezdev/tinygo-bno08x"
)

const (
	// IntervalDuration is the duration of the main loop interval
	IntervalDuration = 100 * time.Millisecond
)

var (
	// quaternionXPrefix is the prefix for the quaternion X value in the debug output
	quaternionXPrefix = []byte("Quaternion X:")

	// quaternionYPrefix is the prefix for the quaternion Y value in the debug output
	quaternionYPrefix = []byte("Quaternion Y:")

	// quaternionZPrefix is the prefix for the quaternion Z value in the debug output
	quaternionZPrefix = []byte("Quaternion Z:")

	// quaternionWPrefix is the prefix for the quaternion W value in the debug output
	quaternionWPrefix = []byte("Quaternion W:")
)

func main() {
	// Wait 5 seconds before starting the test
	time.Sleep(5 * time.Second)

	for {
		// Update quaternion
		internalbno08x.BNO08XSimpleService.Update()

		// Get the quaternion
		q := internalbno08x.BNO08XSimpleService.GetQuaternion()
		x := q[ralvarezdevbno08x.QuaternionXIndex]
		y := q[ralvarezdevbno08x.QuaternionYIndex]
		z := q[ralvarezdevbno08x.QuaternionZIndex]
		w := q[ralvarezdevbno08x.QuaternionWIndex]

		// Log the quaternion values
		internal.Logger.AddMessageWithFloat64(quaternionXPrefix, x, true, true)
		internal.Logger.AddMessageWithFloat64(quaternionYPrefix, y, true, true)
		internal.Logger.AddMessageWithFloat64(quaternionZPrefix, z, true, true)
		internal.Logger.AddMessageWithFloat64(quaternionWPrefix, w, true, true)

		// Sleep for the interval duration
		time.Sleep(IntervalDuration)

		// Print memory stats
		internal.PrintMemory()
	}
}
