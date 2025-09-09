package usbcdc

import (
	tinygotypes "github.com/ralvarezdev/tinygo-types"
)

type (
	// Debug represents the enum debug messages sent and received to the Raspberry Pi 5
	Debug uint8
)

const (
	DebugNil Debug = iota
	DebugReceivedStatus
	DebugReceivedMotorSpeed
	DebugReceivedServoAngle
)

// DebugFromUint8 returns the Debug enum based on a given uint8 value
//
// Parameters:
//
// value: The uint8 value to search on Debugs
//
// Returns:
//
// The Debug enum value, or an error if the key wasn't found for the given value
func DebugFromUint8(value uint8) (Debug, tinygotypes.ErrorCode) {
	switch Debug(value) {
	case DebugNil:
		return DebugNil, tinygotypes.ErrorCodeNil
	case DebugReceivedStatus:
		return DebugReceivedStatus, tinygotypes.ErrorCodeNil
	case DebugReceivedMotorSpeed:
		return DebugReceivedMotorSpeed, tinygotypes.ErrorCodeNil
	case DebugReceivedServoAngle:
		return DebugReceivedServoAngle, tinygotypes.ErrorCodeNil
	default:
		return DebugNil, ErrorCodeUSBCDCInvalidDebugUint8
	}
}