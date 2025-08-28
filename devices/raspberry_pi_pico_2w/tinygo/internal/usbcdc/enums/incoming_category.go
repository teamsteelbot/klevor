package enums

import (
	"fmt"
	"strings"
)

type (
	// IncomingCategory represents the enum categories of incoming messages from the Raspberry Pi 5
	IncomingCategory uint8
)

const (
	IncomingCategoryNil IncomingCategory = iota
	IncomingCategoryStatus
	IncomingCategoryMotorSpeedStop
	IncomingCategoryMotorSpeedForward
	IncomingCategoryMotorSpeedBackward
	IncomingCategoryServoAngleCenter
	IncomingCategoryServoAngleToLeft
	IncomingCategoryServoAngleToRight
)

var (
	// IncomingCategoryNames maps a given IncomingCategory to its string name
	IncomingCategoryNames = map[IncomingCategory]string{
		IncomingCategoryStatus:             "status",
		IncomingCategoryMotorSpeedStop:     "motor_speed_stop",
		IncomingCategoryMotorSpeedForward:  "motor_speed_forward",
		IncomingCategoryMotorSpeedBackward: "motor_speed_backward",
		IncomingCategoryServoAngleCenter:   "servo_angle_center",
		IncomingCategoryServoAngleToLeft:   "servo_angle_to_left",
		IncomingCategoryServoAngleToRight:  "servo_angle_to_right",
	}
)

// String returns the string representation of the IncomingCategory
//
// Returns:
//
// The string representation of the IncomingCategory enum
func (i *IncomingCategory) String() string {
	return IncomingCategoryNames[*i]
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
	if value <= uint8(IncomingCategoryNil) || value > uint8(len(IncomingCategoryNames)) {
		return IncomingCategoryNil, fmt.Errorf(
			ErrInvalidIncomingCategory,
			value,
		)
	}
	return IncomingCategory(value), nil
}

// IsAServoCategory checks if the given IncomingCategory is a servo category
//
// Returns:
//
// True if the category is a servo category, otherwise False
func (i *IncomingCategory) IsAServoCategory() bool {
	return *i == IncomingCategoryServoAngleCenter ||
		*i == IncomingCategoryServoAngleToLeft ||
		*i == IncomingCategoryServoAngleToRight
}

// IsAMotorCategory checks if the given IncomingCategory is a motor category
//
// Returns:
//
// True if the category is a motor category, otherwise False
func (i *IncomingCategory) IsAMotorCategory() bool {
	return *i == IncomingCategoryMotorSpeedStop ||
		*i == IncomingCategoryMotorSpeedForward ||
		*i == IncomingCategoryMotorSpeedBackward
}
