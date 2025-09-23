package internal

import (
	tinygobno08x "github.com/ralvarezdev/tinygo-bno08x"
)

const (
	// Float64Precision defines the precision for float64 values
	Float64Precision = 3
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

// PrintEulerDegrees prints the Euler degrees from the BNO08X sensor
//
// Parameters:
//
// eulerDegrees: A [3]float64 array representing the Euler angles (yaw, pitch, roll) in degrees
func PrintEulerDegrees(eulerDegrees [3]float64) {
	Logger.AddMessage(eulerHeader, true)
	Logger.AddMessageWithFloat64(
		yawDegreesPrefix,
		eulerDegrees[tinygobno08x.EulerDegreesYawIndex],
		Float64Precision,
		true,
		true,
	)
	Logger.AddMessageWithFloat64(
		pitchDegreesPrefix,
		eulerDegrees[tinygobno08x.EulerDegreesPitchIndex],
		Float64Precision,
		true,
		true,
	)
	Logger.AddMessageWithFloat64(
		rollDegreesPrefix,
		eulerDegrees[tinygobno08x.EulerDegreesRollIndex],
		Float64Precision,
		true,
		true,
	)
	Logger.Debug()
}

// PrintQuaternion prints the quaternion values from the BNO08X sensor
//
// Parameters:
//
// quaternion: A [4]float64 array representing the quaternion (x, y, z, w)
func PrintQuaternion(quaternion [4]float64) {
	Logger.AddMessage(quaternionHeader, true)
	Logger.AddMessageWithFloat64(
		quaternionXPrefix,
		quaternion[tinygobno08x.QuaternionXIndex],
		Float64Precision,
		true,
		true,
	)
	Logger.AddMessageWithFloat64(
		quaternionYPrefix,
		quaternion[tinygobno08x.QuaternionYIndex],
		Float64Precision,
		true,
		true,
	)
	Logger.AddMessageWithFloat64(
		quaternionZPrefix,
		quaternion[tinygobno08x.QuaternionZIndex],
		Float64Precision,
		true,
		true,
	)
	Logger.AddMessageWithFloat64(
		quaternionWPrefix,
		quaternion[tinygobno08x.QuaternionWIndex],
		Float64Precision,
		true,
		true,
	)
	Logger.Debug()
}
