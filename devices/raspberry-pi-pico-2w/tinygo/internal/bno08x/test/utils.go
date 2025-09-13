//go:build tinygo && (rp2040 || rp2350)

package tinygo_bno08x

import (
	"time"

	"machine"
)

var (
	// hardwareResetStart is the initial message printed when performing a hardware reset
	hardwareResetStart = []byte("Hardware resetting...")

	// hardwareResetComplete is the message printed when a hardware reset is complete
	hardwareResetComplete = []byte("Hardware reset complete")

	// errorInAfterHardwareResetFn is the message printed when there is an error in the afterHardwareResetFn
	errorInAfterHardwareResetFn = []byte("Error in afterHardwareResetFn:")
)

// HardwareReset performs a hardware reset of the BNO08X sensor to an initial unconfigured state.
//
// Parameters:
//
// reset: The machine.Pin used to perform the hardware reset.
// logger: An optional Logger for logging debug information during the reset process.
func HardwareReset(resetPin machine.Pin, logger Logger) {
	if logger != nil {
		logger.InfoMessage(hardwareResetStart)
	}

	// Configure the reset pin as output
	resetPin.Configure(machine.PinConfig{Mode: machine.PinOutput})

	resetPin.High()
	time.Sleep(ResetPinDelay)

	resetPin.Low()
	time.Sleep(ResetPinDelay)

	resetPin.High()
	time.Sleep(ResetPinDelay)

	if logger != nil {
		logger.InfoMessage(hardwareResetComplete)
	}
}