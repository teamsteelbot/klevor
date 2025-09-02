package enums

import (
	"fmt"
	"strings"
)

type (
	// OutgoingCategory represents the enum categories of outgoing messages from the Raspberry Pi 5
	OutgoingCategory uint8
)

const (
	OutgoingCategoryNil OutgoingCategory = iota
	OutgoingCategoryStatus
	OutgoingCategoryMotorSpeedStop
	OutgoingCategoryMotorSpeedForward
	OutgoingCategoryMotorSpeedBackward
	OutgoingCategoryGetMaxMotorSpeedValue
	OutgoingCategoryServoDirectionCenter
	OutgoingCategoryServoDirectionToLeft
	OutgoingCategoryServoDirectionToRight
	OutgoingCategoryGetMaxServoDirectionValue
)

var (
	// OutgoingCategoryNames maps a given OutgoingCategory to its string name
	OutgoingCategoryNames = map[OutgoingCategory]string{
		OutgoingCategoryStatus:                    "status",
		OutgoingCategoryMotorSpeedStop:            "motor_speed_stop",
		OutgoingCategoryMotorSpeedForward:         "motor_speed_forward",
		OutgoingCategoryMotorSpeedBackward:        "motor_speed_backward",
		OutgoingCategoryGetMaxMotorSpeedValue:     "get_max_motor_speed_value",
		OutgoingCategoryServoDirectionCenter:      "servo_direction_center",
		OutgoingCategoryServoDirectionToLeft:      "servo_direction_to_left",
		OutgoingCategoryServoDirectionToRight:     "servo_direction_to_right",
		OutgoingCategoryGetMaxServoDirectionValue: "get_max_servo_direction_value",
	}
)

// String returns the string representation of the OutgoingCategory
//
// Returns:
//
// The string representation of the OutgoingCategory enum
func (i *OutgoingCategory) String() string {
	return OutgoingCategoryNames[*i]
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
	if value <= uint8(OutgoingCategoryNil) || value > uint8(len(OutgoingCategoryNames)) {
		return OutgoingCategoryNil, fmt.Errorf(
			ErrInvalidOutgoingCategory,
			value,
		)
	}
	return OutgoingCategory(value), nil
}

// IsAServoCategory checks if the given OutgoingCategory is a servo category
//
// Returns:
//
// True if the category is a servo category, otherwise False
func (i *OutgoingCategory) IsAServoCategory() bool {
	return *i == OutgoingCategoryServoDirectionCenter ||
		*i == OutgoingCategoryServoDirectionToLeft ||
		*i == OutgoingCategoryServoDirectionToRight
}

// IsAMotorCategory checks if the given OutgoingCategory is a motor category
//
// Returns:
//
// True if the category is a motor category, otherwise False
func (i *OutgoingCategory) IsAMotorCategory() bool {
	return *i == OutgoingCategoryMotorSpeedStop ||
		*i == OutgoingCategoryMotorSpeedForward ||
		*i == OutgoingCategoryMotorSpeedBackward
}
