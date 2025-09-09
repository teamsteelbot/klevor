//go:build tinygo && (rp2040 || rp2350)

package tinygo_bno08x

import (
	"math"
	"time"

	"machine"
)

// HardwareReset performs a hardware reset of the BNO08X sensor to an initial unconfigured state.
//
// Parameters:
//
// reset: The machine.Pin used to perform the hardware reset.
// debugger: An optional Debugger for logging debug information during the reset process.
// afterHardwareResetFn: An optional function to be called after the hardware reset is complete.
func HardwareReset(resetPin machine.Pin, debugger Debugger, afterHardwareResetFn func() error) {
	if debugger != nil {
		debugger.Debug("Hardware resetting...")
	}

	// Configure the reset pin as output
	resetPin.Configure(machine.PinConfig{Mode: machine.PinOutput})

	resetPin.High()
	time.Sleep(ResetPinDelay)

	resetPin.Low()
	time.Sleep(ResetPinDelay)

	resetPin.High()
	time.Sleep(ResetPinDelay)

	// Call the afterHardwareResetFn if provided
	if afterHardwareResetFn != nil {
		if err := afterHardwareResetFn(); err != nil {
			if debugger != nil {
				debugger.Debug("Error in afterHardwareResetFn:", err)
			}
		}
	}

	if debugger != nil {
		debugger.Debug("Hardware reset complete")
	}
}

// QuaternionToEulerDegrees converts the quaternion representation of orientation to Euler angles (roll, pitch, yaw) in degrees.
//
// Returns:
//
// A tuple of three float64 values representing the roll, pitch, and yaw angles in degrees, or an error if the input is nil.
func QuaternionToEulerDegrees(rotationVector *[4]float64) (*[3]float64, error) {
	// Check if the rotation vector is nil
	if rotationVector == nil {
		return nil, ErrNilRotationVector
	}

	// Get the quaternion components
	x := rotationVector[0]
	y := rotationVector[1]
	z := rotationVector[2]
	w := rotationVector[3]

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
