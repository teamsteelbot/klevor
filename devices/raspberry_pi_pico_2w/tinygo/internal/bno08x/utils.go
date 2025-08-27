package bno08x

import (
	// bno08x "github.com/ralvarezdev/go-bno08x"
	bno08x "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/bno08x/test"
)

// afterReset is a function that is called after the BNO08x sensor is reset.
func afterReset(b *bno08x.BNO08X) error {
	// Check if the BNO08X instance is nil
	if b == nil {
		return bno08x.ErrNilBNO08X
	}

	// Enable quaternion feature
	return b.EnableFeature(bno08x.ReportIDRotationVector)
}
