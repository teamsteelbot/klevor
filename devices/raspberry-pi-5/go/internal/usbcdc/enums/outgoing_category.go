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
	
	// OutgoingCategories maps a given uint8 value to its OutgoingCategory enum
	OutgoingCategories = map[uint8]OutgoingCategory{
		OutgoingCategoryNil.Uint8():  OutgoingCategoryNil,
		OutgoingCategoryStatus.Uint8():  OutgoingCategoryStatus,
		OutgoingCategoryMotorSpeedStop.Uint8():  OutgoingCategoryMotorSpeedStop,
		OutgoingCategoryMotorSpeedForward.Uint8():  OutgoingCategoryMotorSpeedForward,
		OutgoingCategoryMotorSpeedBackward.Uint8():  OutgoingCategoryMotorSpeedBackward,
		OutgoingCategoryGetMaxMotorSpeedValue.Uint8():  OutgoingCategoryGetMaxMotorSpeedValue,
		OutgoingCategoryServoDirectionCenter.Uint8():  OutgoingCategoryServoDirectionCenter,
		OutgoingCategoryServoDirectionToLeft.Uint8():  OutgoingCategoryServoDirectionToLeft,
		OutgoingCategoryServoDirectionToRight.Uint8():  OutgoingCategoryServoDirectionToRight,
		OutgoingCategoryGetMaxServoDirectionValue.Uint8():  OutgoingCategoryGetMaxServoDirectionValue,
	}
)

// Uint8 returns the uint8 representation of the OutgoingCategory
//
// Returns:
//
// The uint8 representation of the OutgoingCategory enum
func (o OutgoingCategory) Uint8() uint8 {
	return uint8(o)
}

// Name returns the name of the OutgoingCategory
//
// Returns:
//
// The name of the OutgoingCategory enum
func (o OutgoingCategory) Name() string {
	return OutgoingCategoryNames[o]
}

// String returns the string representation of the OutgoingCategory
//
// Returns:
//
// The string representation of the OutgoingCategory enum
func (o OutgoingCategory) String() string {
	return fmt.Sprintf("%d", o)
}

// IsAServoCategory checks if the given OutgoingCategory is a servo category
//
// Returns:
//
// True if the category is a servo category, otherwise False
func (o OutgoingCategory) IsAServoCategory() bool {
	return o == OutgoingCategoryServoDirectionCenter ||
		o == OutgoingCategoryServoDirectionToLeft ||
		o == OutgoingCategoryServoDirectionToRight
}

// IsAMotorCategory checks if the given OutgoingCategory is a motor category
//
// Returns:
//
// True if the category is a motor category, otherwise False
func (o OutgoingCategory) IsAMotorCategory() bool {
	return o == OutgoingCategoryMotorSpeedStop ||
		o == OutgoingCategoryMotorSpeedForward ||
		o == OutgoingCategoryMotorSpeedBackward
}


// OutgoingCategoryByName returns the OutgoingCategory enum based on a given string
//
// Parameters:
//
// s: The string name to search on OutgoingCategoryNames
//
// Returns:
//
// The OutgoingCategory enum value, or an error if the key wasn't found for the given value
func OutgoingCategoryByName(s string) (OutgoingCategory, error) {
	// Format the string
	s = strings.ToLower(strings.TrimSpace(s))

	// Search for the given incoming category name
	for key, value := range OutgoingCategoryNames {
		if value == s {
			return key, nil
		}
	}
	return OutgoingCategoryNil, fmt.Errorf(ErrInvalidOutgoingCategoryName, s)
}

// OutgoingCategoryFromString returns the OutgoingCategory enum based on a given string
//
// Parameters:
//
// s: The string to parse as OutgoingCategory
//
// Returns:
//
// The OutgoingCategory enum value, or an error if the key wasn't found for the given value
func OutgoingCategoryFromString(s string) (OutgoingCategory, error) {
	// Format the string
	s = strings.ToLower(strings.TrimSpace(s))

	// Try to parse as uint8 first
	var value uint8
	if _, err := fmt.Sscanf(s, "%d", &value); err != nil {
		return OutgoingCategoryNil, fmt.Errorf(ErrInvalidOutgoingCategoryString, s)
	}

	// If the string was a number, try to get the OutgoingCategory from the uint8 value
	category, err := OutgoingCategoryFromUint8(value);
	if err != nil {
		return OutgoingCategoryNil, err
	}
	return category, nil
}

// OutgoingCategoryFromUint8 returns the OutgoingCategory enum based on a given uint8 value
//
// Parameters:
//
// value: The uint8 value to search on OutgoingCategories
//
// Returns:
//
// The OutgoingCategory enum value, or an error if the key wasn't found for the given value
func OutgoingCategoryFromUint8(value uint8) (OutgoingCategory, error) {
	category, ok := OutgoingCategories[value]
	if !ok {
		return OutgoingCategoryNil, fmt.Errorf(ErrInvalidOutgoingCategoryUint8, value)
	}
	return category, nil
}