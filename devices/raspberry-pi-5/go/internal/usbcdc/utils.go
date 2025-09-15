package usbcdc

import (
	"math"

	gotinygoerrors "github.com/ralvarezdev/go-tinygo-errors"
	tinygoerrors "github.com/ralvarezdev/tinygo-errors"
)

// QuaternionToEulerDegrees converts the quaternion representation of orientation to Euler angles (roll, pitch, yaw) in degrees.
//
// Parameters:
//
// quaternion: A [4]float64 array representing the quaternion (x, y, z, w)
//
// Returns:
//
// A tuple of three float64 values representing the roll, pitch, and yaw angles in degrees
func QuaternionToEulerDegrees(quaternion [4]float64) [3]float64 {
	// Get the quaternion components
	x := quaternion[QuaternionXIndex]
	y := quaternion[QuaternionYIndex]
	z := quaternion[QuaternionZIndex]
	w := quaternion[QuaternionWIndex]

	// Roll (X axis)
	sinRollCosPitch := 2 * (w*x + y*z)
	cosRollCosPitch := 1 - 2*(x*x+y*y)
	roll := math.Atan2(sinRollCosPitch, cosRollCosPitch)

	// Pitch (Y axis)
	sinPitch := 2 * (w*y - z*x)
	var pitch float64
	if sinPitch >= 1 {
		pitch = math.Pi / 2
	} else if sinPitch <= -1 {
		pitch = -math.Pi / 2
	} else {
		pitch = math.Asin(sinPitch)
	}

	// Yaw (Z axis)
	sinYawCosPitch := 2 * (w*z + x*y)
	cosYawCosPitch := 1 - 2*(y*y+z*z)
	yaw := math.Atan2(sinYawCosPitch, cosYawCosPitch)

	// Create the euler degrees array and convert radians to degrees
	var eulerDegrees [3]float64
	eulerDegrees[EulerDegreesRollIndex] = roll * 180 / math.Pi
	eulerDegrees[EulerDegreesPitchIndex] = pitch * 180 / math.Pi
	eulerDegrees[EulerDegreesYawIndex] = yaw * 180 / math.Pi

	return eulerDegrees
}

// GetErrorCodeMessage retrieves the error message corresponding to a given error code
//
// Parameters:
//
// errorCode: The error code to look up
//
// Returns:
//
// The corresponding error message if found, otherwise an empty string, and a boolean indicating if the message was found
func GetErrorCodeMessage(errorCode tinygoerrors.ErrorCode) (string, bool) {
	if errorMessage, ok := gotinygoerrors.ErrorCodeMessages[errorCode]; ok {
		return errorMessage, true
	} else if internalErrorMessage, ok := tinygoerrors.ErrorCodeMessages[errorCode]; ok {
		return internalErrorMessage, true
	}
	return "", false
}
