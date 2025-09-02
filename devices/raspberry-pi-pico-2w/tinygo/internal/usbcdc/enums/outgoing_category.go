package enums

import (
	"fmt"
	"strings"
)

type (
	// OutgoingCategory represents the enum categories of outgoing messages to the Raspberry Pi 5
	OutgoingCategory uint8
)

const (
	OutgoingCategoryNil OutgoingCategory = iota
	OutgoingCategoryChallenge
	OutgoingCategoryStatus
	OutgoingCategoryBNO08XYawDegrees
	OutgoingCategoryBNO08XYawTurns
	OutgoingCategoryError
	OutgoingCategoryDebug
	OutgoingCategoryMaxMotorSpeedValue
	OutgoingCategoryMaxServoDirectionValue
)

var (
	// OutgoingCategoryNames maps a given OutgoingCategory to its string name
	OutgoingCategoryNames = map[OutgoingCategory]string{
		OutgoingCategoryChallenge:              "challenge",
		OutgoingCategoryStatus:                 "status",
		OutgoingCategoryBNO08XYawDegrees:       "bno08x_yaw_deg",
		OutgoingCategoryBNO08XYawTurns:         "bno08x_yaw_turns",
		OutgoingCategoryError:                  "error",
		OutgoingCategoryDebug:                  "debug",
		OutgoingCategoryMaxMotorSpeedValue:     "max_motor_speed_value",
		OutgoingCategoryMaxServoDirectionValue: "max_servo_direction_value",
	}
)

// String returns the string representation of the OutgoingCategory
//
// Returns:
//
// The string representation of the OutgoingCategory enum
func (o OutgoingCategory) String() string {
	return OutgoingCategoryNames[o]
}

// OutgoingCategoryFromString returns the OutgoingCategory enum based on a given string
//
// Parameters:
//
// s: The string name to search on OutgoingCategoryNames
//
// Returns:
//
// The OutgoingCategory enum value, or an error if the key wasn't found for the given value
func OutgoingCategoryFromString(s string) (OutgoingCategory, error) {
	// Format the string
	s = strings.ToLower(strings.TrimSpace(s))

	// Search for the given outgoing category name
	for key, value := range OutgoingCategoryNames {
		if value == s {
			return key, nil
		}
	}
	return OutgoingCategoryNil, fmt.Errorf(ErrInvalidOutgoingCategoryName, s)
}

// OutgoingCategoryFromUint8 returns the OutgoingCategory enum based on a given uint8 value
//
// Parameters:
//
// value: The uint8 value to search on OutgoingCategoryNames
//
// Returns:
//
// The OutgoingCategory enum value, or an error if the key wasn't found for the given value
func OutgoingCategoryFromUint8(value uint8) (OutgoingCategory, error) {
	if value <= uint8(OutgoingCategoryNil) || value >= uint8(len(OutgoingCategoryNames)) {
		return OutgoingCategoryNil, fmt.Errorf(
			ErrInvalidOutgoingCategory,
			value,
		)
	}
	return OutgoingCategory(value), nil
}
