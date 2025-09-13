package bno08x

import (
	tinygobno08x "github.com/ralvarezdev/tinygo-bno08x"
	tinygotypes "github.com/ralvarezdev/tinygo-types"
)

// afterReset is a function that is called after a reset of the BNO08X sensor.
//
// Returns:
//
// An error if the BNO08X instance is nil or if enabling the quaternion feature fails.
func afterReset(b *tinygobno08x.BNO08X) tinygotypes.ErrorCode {
	// Check if the BNO08X instance is nil
	if b == nil {
		return tinygobno08x.ErrorCodeBNO08XNilBNO08XInstance
	}

	// Enable quaternion feature
	return b.EnableFeature(tinygobno08x.ReportIDRotationVector)
}
