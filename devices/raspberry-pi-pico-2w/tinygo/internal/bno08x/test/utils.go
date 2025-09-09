//go:build tinygo && (rp2040 || rp2350)

package tinygo_bno08x

import (
	"time"

	"machine"

	tinygotypes "github.com/ralvarezdev/tinygo-types"
)

// HardwareReset performs a hardware reset of the BNO08X sensor to an initial unconfigured state.
//
// Parameters:
//
// reset: The machine.Pin used to perform the hardware reset.
// debugger: An optional Debugger for logging debug information during the reset process.
// afterHardwareResetFn: An optional function to be called after the hardware reset is complete.
func HardwareReset(resetPin machine.Pin, debugger Debugger, afterHardwareResetFn func() tinygotypes.ErrorCode) {
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
		if err := afterHardwareResetFn(); err != tinygotypes.ErrorCodeNil {
			if debugger != nil {
				debugger.Debug("Error in afterHardwareResetFn:", err)
			}
		}
	}

	if debugger != nil {
		debugger.Debug("Hardware reset complete")
	}
}