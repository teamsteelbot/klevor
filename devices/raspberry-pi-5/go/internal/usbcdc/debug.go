package enums

import (
	"fmt"
	"strings"
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

var (
	// DebugNames maps a given Debug to its string name
	DebugNames = map[Debug]string{
		DebugReceivedStatus:     "received_status",
		DebugReceivedMotorSpeed: "received_motor_speed",
		DebugReceivedServoAngle: "received_servo_angle",
	}

	// Debugs maps a given uint8 value to its Debug enum
	Debugs = map[uint8]Debug{
		DebugNil.Uint8():           DebugNil,
		DebugReceivedStatus.Uint8():     DebugReceivedStatus,
		DebugReceivedMotorSpeed.Uint8(): DebugReceivedMotorSpeed,
		DebugReceivedServoAngle.Uint8(): DebugReceivedServoAngle,
	}
)

// Uint8 returns the uint8 representation of the Debug
//
// Returns:
//
// The uint8 representation of the Debug enum
func (d Debug) Uint8() uint8 {
	return uint8(d)
}

// Name returns the name of the Debug
//
// Returns:
//
// The name of the Debug enum
func (d Debug) Name() string {
	return DebugNames[d]
}


// String returns the string representation of the Debug
//
// Returns:
//
// The string representation of the Debug enum
func (d Debug) String() string {
	return fmt.Sprintf("%d", d)
}

// DebugByName returns the Debug enum based on a given string
//
// Parameters:
//
// s: The string name to search on DebugNames
//
// Returns:
//
// The Debug enum value, or an error if the key wasn't found for the given value
func DebugByName(s string) (Debug, error) {
	// Format the string
	s = strings.ToLower(strings.TrimSpace(s))

	// Search for the given debug name
	for key, value := range DebugNames {
		if value == s {
			return key, nil
		}
	}
	return DebugNil, fmt.Errorf(ErrInvalidDebugName, s)
}


// DebugFromString returns the Debug enum based on a given string
//
// Parameters:
//
// s: The string to parse as Debug
//
// Returns:
//
// The Debug enum value, or an error if the key wasn't found for the given value
func DebugFromString(s string) (Debug, error) {
	// Format the string
	s = strings.ToLower(strings.TrimSpace(s))

	// Try to parse as uint8 first
	var value uint8
	if _, err := fmt.Sscanf(s, "%d", &value); err != nil {
		return DebugNil, fmt.Errorf(ErrInvalidDebugString, s)
	}

	// If the string was a number, try to get the Debug from the uint8 value
	category, err := DebugFromUint8(value);
	if err != nil {
		return DebugNil, err
	}
	return category, nil
}

// DebugFromUint8 returns the Debug enum based on a given uint8 value
//
// Parameters:
//
// value: The uint8 value to search on Debugs
//
// Returns:
//
// The Debug enum value, or an error if the key wasn't found for the given value
func DebugFromUint8(value uint8) (Debug, error) {
	category, ok := Debugs[value]
	if !ok {
		return DebugNil, fmt.Errorf(ErrInvalidDebugUint8, value)
	}
	return category, nil
}