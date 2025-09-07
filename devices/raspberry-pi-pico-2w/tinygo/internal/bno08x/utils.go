package bno08x

import (
	ralvarezdevbno08x "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/bno08x/test"
	//ralvarezdevbno08x "github.com/ralvarezdev/go-bno08x"
)

// afterReset is a function that is called after the BNO08x sensor is reset.
func afterReset(b *ralvarezdevbno08x.BNO08X) error {
	// Check if the BNO08X instance is nil
	if b == nil {
		return ralvarezdevbno08x.ErrNilBNO08X
	}

	// Enable quaternion feature
	return b.EnableFeature(ralvarezdevbno08x.ReportIDRotationVector)
}
