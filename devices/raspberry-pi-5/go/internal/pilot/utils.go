package pilot

import (
	"math"

	"github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal"
)



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