package pilot

import (
	"math"

	"github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal"
)

// CalculateAverageDistanceFromAngle calculates the average distance for a given list of angles.
//
// Parameters:
//
// measures: A pointer to an array of 360 Measure pointers indexed by angle.
// middleAngle: The middle angle to start the averaging from.
// width: The sum of the angles to consider with both sides and the middle angle.
//
// Returns:
//
// The average distance for the specified angles, or an error if the width is not valid.
func CalculateAverageDistanceFromAngle(
	measures *[360]*internal.Measure,
	middleAngle int,
	width int,
) (float64, error) {
	var totalDistance float64
	var count int

	// Calculate the range of angles to consider
	if width%2 == 0 {
		return 0, ErrAngleWidthMustBeOdd
	}
	if width < 1 {
		return 0, ErrAngleWidthTooSmall
	}
	if width >= 360 {
		return 0, ErrAngleWidthTooLarge
	}

	// Check if the width is 1, in which case we only consider the middle angle
	if width == 1 {
		measure := measures[middleAngle]
		if measure == nil {
			return 0.0, nil
		}
		return measure.GetDistance(), nil
	}

	// Calculate the angles to consider
	var angles []int
	widthPerSide := (width - 1) / 2
	leftAngle := middleAngle - widthPerSide
	rightAngle := middleAngle + widthPerSide
	if leftAngle < 0 {
		for angle := 360 + leftAngle; angle < 360; angle++ {
			angles = append(angles, angle)
		}
	}
	if rightAngle >= 360 {
		for angle := 0; angle <= rightAngle-360; angle++ {
			angles = append(angles, angle)
		}
	}
	for angle := max(leftAngle, 0); angle <= min(360, rightAngle); angle++ {
		angles = append(angles, angle)
	}

	// Calculate the average distance
	for _, angle := range angles {
		measure := measures[angle]
		if measure == nil {
			continue
		}

		// Check the distance and quality
		if measure.GetDistance() == 0.0 || measure.GetQuality() == 0 {
			continue
		}

		totalDistance += measure.GetDistance()
		count++
	}
	return totalDistance / float64(count), nil
}

// CalculateAverageDistanceFromDirection calculates the average distance for a given direction.
//
// Parameters:
//
// measures: A pointer to an array of 360 Measure pointers indexed by angle.
// direction: The direction to calculate the average distance for.
// width: The sum of the angles to consider with both sides and the middle angle.
//
// Returns:
//
// The average distance for the specified direction, or an error if the direction is not valid.
func CalculateAverageDistanceFromDirection(
	measures *[360]*internal.Measure,
	direction CardinalDirection,
	width int,
) (float64, error) {
	directionAngle := direction.Angle()

	// Round the angle
	if directionAngle >= 180 {
		directionAngle = math.Ceil(directionAngle)
	} else {
		directionAngle = math.Floor(directionAngle)
	}

	return CalculateAverageDistanceFromAngle(
		measures,
		int(directionAngle),
		width,
	)
}

// CalculateAverageDistances calculates the average distances for the specified directions.
//
// Parameters:
//
// measures: A pointer to an array of 360 Measure pointers indexed by angle.
// width: The sum of the angles to consider with both sides and the middle angle.
// directions: The directions to calculate the average distances for.
//
// Returns:
//
// A map with directions as keys and their average distances as values, or an error if any direction is not valid.
func CalculateAverageDistances(
	measures *[360]*internal.Measure,
	width int,
	directions ...CardinalDirection,
) (map[CardinalDirection]float64, error) {
	avgDistances := make(map[CardinalDirection]float64)
	for _, direction := range directions {
		avgDistance, err := CalculateAverageDistanceFromDirection(
			measures, direction, width,
		)
		if err != nil {
			return nil, err
		}
		avgDistances[direction] = avgDistance
	}
	return avgDistances, nil
}

// QuaternionToEulerDegrees converts the quaternion representation of orientation to Euler angles (roll, pitch, yaw) in degrees.
//
// Returns:
//
// A tuple of three float64 values representing the roll, pitch, and yaw angles in degrees, or an error if the input is nil.
func QuaternionToEulerDegrees(quaternion *[4]float64) (*[3]float64, error) {
	// Check if the quaternion is nil
	if quaternion == nil {
		return nil, ErrNilQuaternion
	}

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

	return &[3]float64{
		roll * 180 / math.Pi,
		pitch * 180 / math.Pi,
		yaw * 180 / math.Pi,
	}, nil
}

// Update roll, pitch, and yaw degrees
	h.lastYawDegrees = h.yawDegrees
	h.eulerDegrees = eulerDegrees
	h.rollDegrees = eulerDegrees[ralvarezdevbno08x.EulerDegreesRollIndex]
	h.pitchDegrees = eulerDegrees[ralvarezdevbno08x.EulerDegreesPitchIndex]
	h.yawDegrees = eulerDegrees[ralvarezdevbno08x.EulerDegreesYawIndex]

	// Send the yaw degrees message via USB CDC if enabled
	if h.usbCDCHandler != nil {
		// Only send if the yaw has changed significantly
		hasChanged := false
		if h.yawDegrees > h.lastYawDegrees && h.yawDegrees > h.lastYawDegrees+YawDegreesDifference {
			hasChanged = true
		} else if h.yawDegrees < h.lastYawDegrees && h.yawDegrees < h.lastYawDegrees-YawDegreesDifference {
			hasChanged = true
		}

		// Send the yaw degrees message if it has changed
		if hasChanged {
			if err := h.usbCDCHandler.SendBNO08XYawDegreesMessage(h.yawDegrees); err != nil {
				return err
			}
		}
	}

	// Update internal yaw state
	relativeYawDegrees := h.yawDegrees - h.initialEulerDegrees[ralvarezdevbno08x.EulerDegreesYawIndex]
	if relativeYawDegrees > 180 {
		relativeYawDegrees -= 360
	} else if relativeYawDegrees < -180 {
		relativeYawDegrees += 360
	}

	// Calculate the change in yaw degrees since the last update
	deltaRawYawDegrees := relativeYawDegrees - h.lastRelativeYawDegrees
	if deltaRawYawDegrees > 180 {
		deltaRawYawDegrees -= 360
	} else if deltaRawYawDegrees < -180 {
		deltaRawYawDegrees += 360
	}

	// Update accumulated yaw and segment count
	h.accumulatedYawDegrees += deltaRawYawDegrees
	currentSegmentCount := int(h.accumulatedYawDegrees / 90)
	if currentSegmentCount != h.lastSegmentCount {
		h.accumulatedYaw90DegreesTurns += currentSegmentCount - h.lastSegmentCount
		h.lastSegmentCount = currentSegmentCount

		// If serial communication is enabled, send the turn message
		if h.usbCDCHandler != nil {
			if err := h.usbCDCHandler.SendBNO08XYawTurnsMessage(
				h.accumulatedYaw90DegreesTurns,
			); err != nil {
				return err
			}
		}
	}

	// Update the last yaw degrees
	h.lastRelativeYawDegrees = relativeYawDegrees
	return nil