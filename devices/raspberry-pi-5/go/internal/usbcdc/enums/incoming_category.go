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

	// IncomingCategories maps a given uint8 value to its IncomingCategory enum
	IncomingCategories = map[uint8]IncomingCategory{
		IncomingCategoryNil.Uint8():           IncomingCategoryNil,
		IncomingCategoryChallenge.Uint8():     IncomingCategoryChallenge,
		IncomingCategoryStatus.Uint8():        IncomingCategoryStatus,
		IncomingCategoryBNO08XYawDegrees.Uint8():  IncomingCategoryBNO08XYawDegrees,
		IncomingCategoryBNO08XYawTurns.Uint8():    IncomingCategoryBNO08XYawTurns,
		IncomingCategoryError.Uint8():         IncomingCategoryError,
		IncomingCategoryDebug.Uint8():         IncomingCategoryDebug,
		IncomingCategoryMaxMotorSpeedValue.Uint8():    IncomingCategoryMaxMotorSpeedValue,
		IncomingCategoryMaxServoDirectionValue.Uint8(): IncomingCategoryMaxServoDirectionValue,
	}
)

// Uint8 returns the uint8 representation of the IncomingCategory
//
// Returns:
//
// The uint8 representation of the IncomingCategory enum
func (i IncomingCategory) Uint8() uint8 {
	return uint8(i)
}

// Name returns the name of the IncomingCategory
//
// Returns:
//
// The name of the IncomingCategory enum
func (i IncomingCategory) Name() string {
	return IncomingCategoryNames[i]
}

// String returns the string representation of the IncomingCategory
//
// Returns:
//
// The string representation of the IncomingCategory enum
func (i IncomingCategory) String() string {
	return fmt.Sprintf("%d", i)
}

// IncomingCategoryByName returns the IncomingCategory enum based on a given string
//
// Parameters:
//
// s: The string name to search on IncomingCategoryNames
//
// Returns:
//
// The IncomingCategory enum value, or an error if the key wasn't found for the given value
func IncomingCategoryByName(s string) (IncomingCategory, error) {
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

// IncomingCategoryFromString returns the IncomingCategory enum based on a given string
//
// Parameters:
//
// s: The string to parse as IncomingCategory
//
// Returns:
//
// The IncomingCategory enum value, or an error if the key wasn't found for the given value
func IncomingCategoryFromString(s string) (IncomingCategory, error) {
	// Format the string
	s = strings.ToLower(strings.TrimSpace(s))

	// Try to parse as uint8 first
	var value uint8
	if _, err := fmt.Sscanf(s, "%d", &value); err != nil {
		return IncomingCategoryNil, fmt.Errorf(ErrInvalidIncomingCategoryString, s)
	}

	// If the string was a number, try to get the IncomingCategory from the uint8 value
	category, err := IncomingCategoryFromUint8(value);
	if err != nil {
		return IncomingCategoryNil, err
	}
	return category, nil
}

// IncomingCategoryFromUint8 returns the IncomingCategory enum based on a given uint8 value
//
// Parameters:
//
// value: The uint8 value to search on IncomingCategories
//
// Returns:
//
// The IncomingCategory enum value, or an error if the key wasn't found for the given value
func IncomingCategoryFromUint8(value uint8) (IncomingCategory, error) {
	category, ok := IncomingCategories[value]
	if !ok {
		return IncomingCategoryNil, fmt.Errorf(ErrInvalidIncomingCategoryUint8, value)
	}
	return category, nil
}