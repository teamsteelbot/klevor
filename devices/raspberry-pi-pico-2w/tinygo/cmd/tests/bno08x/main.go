package main

import (
	"time"

	"github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal"
	internalbno08x "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/bno08x"
	tinygobno08x "github.com/ralvarezdev/tinygo-bno08x"
)

const (
	// IntervalDuration is the duration of the main loop interval
	IntervalDuration = 100 * time.Millisecond
)

var (
	// quaternionHeader is the header for the quaternion values in the debug output
	quaternionHeader = []byte("QUATERNION VALUES")

	// quaternionXPrefix is the prefix for the quaternion X value in the debug output
	quaternionXPrefix = []byte("\tQuaternion X:")

	// quaternionYPrefix is the prefix for the quaternion Y value in the debug output
	quaternionYPrefix = []byte("\tQuaternion Y:")

	// quaternionZPrefix is the prefix for the quaternion Z value in the debug output
	quaternionZPrefix = []byte("\tQuaternion Z:")

	// quaternionWPrefix is the prefix for the quaternion W value in the debug output
	quaternionWPrefix = []byte("\tQuaternion W:")

	// eulerHeader is the header for the euler angles values in the debug output
	eulerHeader = []byte("EULER ANGLES")

	// yawDegreesPrefix is the prefix for the yaw degrees value in the debug output
	yawDegreesPrefix = []byte("\tYaw Degrees:")

	// pitchDegreesPrefix is the prefix for the pitch degrees value in the debug output
	pitchDegreesPrefix = []byte("\tPitch Degrees:")

	// rollDegreesPrefix is the prefix for the roll degrees value in the debug output
	rollDegreesPrefix = []byte("\tRoll Degrees:")
)

func main() {
	// Check if both BNO08x interfaces are not initialized
	if internalbno08x.UART == nil && internalbno08x.UARTRVC == nil {
		return
	}

	for {
		/*
		if internalbno08x.UART != nil {
			// Update quaternion
			internalbno08x.UART.Update()

			// Get the quaternion
			q := internalbno08x.UART.GetQuaternion()
			x := q[tinygobno08x.QuaternionXIndex]
			y := q[tinygobno08x.QuaternionYIndex]
			z := q[tinygobno08x.QuaternionZIndex]
			w := q[tinygobno08x.QuaternionWIndex]

			// Log the quaternion values
			internal.Logger.AddMessage(quaternionHeader, true)
			internal.Logger.AddMessageWithFloat64(quaternionXPrefix, x, true, true)
			internal.Logger.AddMessageWithFloat64(quaternionYPrefix, y, true, true)
			internal.Logger.AddMessageWithFloat64(quaternionZPrefix, z, true, true)
			internal.Logger.AddMessageWithFloat64(quaternionWPrefix, w, true, true)
			internal.Logger.Debug()
		}
		*/

		if internalbno08x.UARTRVC != nil {
			// Update euler degrees
			internalbno08x.UARTRVC.Update()

			// Get the euler degrees
			e := internalbno08x.UARTRVC.GetEulerDegrees()
			yaw := e[tinygobno08x.EulerDegreesYawIndex]
			pitch := e[tinygobno08x.EulerDegreesPitchIndex]
			roll := e[tinygobno08x.EulerDegreesRollIndex]

			// Log the euler degrees values
			internal.Logger.AddMessage(eulerHeader, true)
			internal.Logger.AddMessageWithFloat64(yawDegreesPrefix, yaw, true, true)
			internal.Logger.AddMessageWithFloat64(pitchDegreesPrefix, pitch, true, true)
			internal.Logger.AddMessageWithFloat64(rollDegreesPrefix, roll, true, true)
			internal.Logger.Debug()
		}

		// Sleep for the interval duration
		time.Sleep(IntervalDuration)

		// Print memory stats
		internal.PrintMemory()
	}
}
