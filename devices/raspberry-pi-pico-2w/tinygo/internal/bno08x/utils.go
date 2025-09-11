package bno08x

import (
	ralvarezdevbno08x "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/bno08x/test"
	//ralvarezdevbno08x "github.com/ralvarezdev/tinygo-bno08x"
	tinygotypes "github.com/ralvarezdev/tinygo-types"
)

// afterReset is a function that is called after a reset of the BNO08X sensor.
//
// Returns:
//
// An error if the BNO08X instance is nil or if enabling the quaternion feature fails.
func afterReset(b *ralvarezdevbno08x.BNO08X) tinygotypes.ErrorCode {
	// Check if the BNO08X instance is nil
	if b == nil {
		return ralvarezdevbno08x.ErrorCodeBNO08XNilBNO08XInstance
	}

	// Enable quaternion feature
	return b.EnableFeature(ralvarezdevbno08x.ReportIDRotationVector)
}
