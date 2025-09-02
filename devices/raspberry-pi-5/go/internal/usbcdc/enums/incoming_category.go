package enums

import (
	"fmt"
	"strings"
)

type (
	// IncomingCategory represents the enum categories of incoming messages to the Raspberry Pi 5
	IncomingCategory uint8
)

const (
	IncomingCategoryNil IncomingCategory = iota
	IncomingCategoryChallenge
	IncomingCategoryStatus
	IncomingCategoryBNO08XYawDegrees
	IncomingCategoryBNO08XYawTurns
	IncomingCategoryError
	IncomingCategoryDebug
	IncomingCategoryMaxMotorSpeedValue
	IncomingCategoryMaxServoDirectionValue
)

var (
	// IncomingCategoryNames maps a given IncomingCategory to its string name
	IncomingCategoryNames = map[IncomingCategory]string{
		IncomingCategoryChallenge:              "challenge",
		IncomingCategoryStatus:                 "status",
		IncomingCategoryBNO08XYawDegrees:       "bno08x_yaw_deg",
		IncomingCategoryBNO08XYawTurns:         "bno08x_yaw_turns",
		IncomingCategoryError:                  "error",
		IncomingCategoryDebug:                  "debug",
		IncomingCategoryMaxMotorSpeedValue:     "max_motor_speed_value",
		IncomingCategoryMaxServoDirectionValue: "max_servo_direction_value",
	}
)

// String returns the string representation of the IncomingCategory
//
// Returns:
//
// The string representation of the IncomingCategory enum
func (o IncomingCategory) String() string {
	return IncomingCategoryNames[o]
}

// IncomingCategoryFromString returns the IncomingCategory enum based on a given string
//
// Parameters:
//
// s: The string name to search on IncomingCategoryNames
//
// Returns:
//
// The IncomingCategory enum value, or an error if the key wasn't found for the given value
func IncomingCategoryFromString(s string) (IncomingCategory, error) {
	// Format the string
	s = strings.ToLower(strings.TrimSpace(s))

	// Search for the given incoming category name
	for key, value := range IncomingCategoryNames {
		if value == s {
			return key, nil
		}
	}
	return IncomingCategoryNil, fmt.Errorf(ErrInvalidIncomingCategoryName, s)
}

// IncomingCategoryFromUint8 returns the IncomingCategory enum based on a given uint8 value
//
// Parameters:
//
// value: The uint8 value to search on IncomingCategoryNames
//
// Returns:
//
// The IncomingCategory enum value, or an error if the key wasn't found for the given value
func IncomingCategoryFromUint8(value uint8) (IncomingCategory, error) {
	if value <= uint8(IncomingCategoryNil) || value >= uint8(len(IncomingCategoryNames)) {
		return IncomingCategoryNil, fmt.Errorf(
			ErrInvalidIncomingCategory,
			value,
		)
	}
	return IncomingCategory(value), nil
}
