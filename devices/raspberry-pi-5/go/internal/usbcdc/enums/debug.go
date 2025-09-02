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
)

// String returns the string representation of the Debug
//
// Returns:
//
// The string representation of the Debug enum
func (d Debug) String() string {
	return DebugNames[d]
}

// DebugFromString returns the Debug enum based on a given string
//
// Parameters:
//
// s: The string name to search on DebugNames
//
// Returns:
//
// The Debug enum value, or an error if the key wasn't found for the given value
func DebugFromString(s string) (Debug, error) {
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
