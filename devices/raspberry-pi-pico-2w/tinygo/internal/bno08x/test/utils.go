//go:build tinygo && (rp2040 || rp2350)

package tinygo_bno08x

import (
	"time"
	"strconv"
	"strings"

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
				debugger.Debug("Error in afterHardwareResetFn: " + uint16ToHex(uint16(err)))
			}
		}
	}

	if debugger != nil {
		debugger.Debug("Hardware reset complete")
	}
}

// uint8ToString converts a uint8 value to its string representation.
//
// Parameters:
//
// value: The uint8 value to convert.
//
// Returns:
//
// A string representation of the uint8 value.
func uint8ToString(value uint8) string {
	return strconv.FormatUint(uint64(value), 10)
}

// uint8ToHex converts a uint8 value to its hexadecimal string representation.
//
// Parameters:
//
// value: The uint8 value to convert.
//
// Returns:
//
// A hexadecimal string representation of the uint8 value.
func uint8ToHex(value uint8) string {
	return "0x" + strings.ToUpper(strconv.FormatUint(uint64(value), 16))
}

// uint16ToString converts a uint16 value to its string representation.
//
// Parameters:
//
// value: The uint16 value to convert.
//
// Returns:
//
// A string representation of the uint16 value.
func uint16ToString(value uint16) string {
	return strconv.FormatUint(uint64(value), 10)
}

// uint16ToHex converts a uint16 value to its hexadecimal string representation.
//
// Parameters:
//
// value: The uint16 value to convert.
//
// Returns:
//
// A hexadecimal string representation of the uint16 value.
func uint16ToHex(value uint16) string {
	return "0x" + strings.ToUpper(strconv.FormatUint(uint64(value), 16))
}

// uint32ToString converts a uint32 value to its string representation.
//
// Parameters:
//
// value: The uint32 value to convert.
//
// Returns:
//
// A string representation of the uint32 value.
func uint32ToString(value uint32) string {
	return strconv.FormatUint(uint64(value), 10)
}

// intToString converts an int value to its string representation.
//
// Parameters:
//
// value: The int value to convert.
//
// Returns:
//
// A string representation of the int value.
func intToString(value int) string {
	return strconv.Itoa(value)
}