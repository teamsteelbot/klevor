package usbcdc

import (
	"math"
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
	x := quaternion[0]
	y := quaternion[1]
	z := quaternion[2]
	w := quaternion[3]

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

	return [3]float64{
		roll * 180 / math.Pi,
		pitch * 180 / math.Pi,
		yaw * 180 / math.Pi,
	}
}

// UpdateTurnsFromYawDegrees updates the calculated number of 90-degree turns based on the current yaw angle in degrees
//
// Parameters:
//
// yawDegrees: The current yaw angle in degrees
// calculatedTurns: Pointer to the current number of 90-degree turns made (can be positive or negative)
//
// Returns:
//
// An error if calculatedTurns is nil, otherwise nil
func UpdateTurnsFromYawDegrees(yawDegrees float64, calculatedTurns *CalculatedTurns) error {
	// Check if calculatedTurns is nil
	if calculatedTurns == nil {
		return ErrNilCalculatedTurns
	}

	// Update internal yaw state
	relativeYawDegrees := yawDegrees - calculatedTurns.GetInitialYawDegrees()
	if relativeYawDegrees > 180 {
		relativeYawDegrees -= 360
	} else if relativeYawDegrees < -180 {
		relativeYawDegrees += 360
	}

	// Calculate the change in yaw degrees since the last update
	deltaRawYawDegrees := relativeYawDegrees - calculatedTurns.GetLastRelativeYawDegrees()
	if deltaRawYawDegrees > 180 {
		deltaRawYawDegrees -= 360
	} else if deltaRawYawDegrees < -180 {
		deltaRawYawDegrees += 360
	}

	// Update accumulated yaw and segment count
	calculatedTurns.UpdateAccumulatedYawDegrees(deltaRawYawDegrees)
	currentSegmentCount := int(calculatedTurns.GetAccumulatedYawDegrees() / 90)

	// Update the last segment count and accumulated turns if the segment count has changed
	lastSegmentCount := calculatedTurns.GetLastSegmentCount()
	if currentSegmentCount != lastSegmentCount {
		calculatedTurns.UpdateAccumulatedYaw90DegreesTurns(currentSegmentCount - lastSegmentCount)
		calculatedTurns.SetLastSegmentCount(currentSegmentCount)
	}

	// Update the last yaw degrees and last relative yaw degrees
	calculatedTurns.SetLastYawDegrees(yawDegrees)
	calculatedTurns.SetLastRelativeYawDegrees(relativeYawDegrees)
	return nil
}
