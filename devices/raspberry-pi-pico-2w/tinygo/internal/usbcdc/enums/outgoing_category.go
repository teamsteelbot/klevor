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

	// OutgoingCategories maps a given uint8 value to its OutgoingCategory enum
	OutgoingCategories = map[uint8]OutgoingCategory{
		OutgoingCategoryNil.Uint8():           OutgoingCategoryNil,
		OutgoingCategoryChallenge.Uint8():     OutgoingCategoryChallenge,
		OutgoingCategoryStatus.Uint8():        OutgoingCategoryStatus,
		OutgoingCategoryBNO08XYawDegrees.Uint8():  OutgoingCategoryBNO08XYawDegrees,
		OutgoingCategoryBNO08XYawTurns.Uint8():    OutgoingCategoryBNO08XYawTurns,
		OutgoingCategoryError.Uint8():         OutgoingCategoryError,
		OutgoingCategoryDebug.Uint8():         OutgoingCategoryDebug,
		OutgoingCategoryMaxMotorSpeedValue.Uint8():    OutgoingCategoryMaxMotorSpeedValue,
		OutgoingCategoryMaxServoDirectionValue.Uint8(): OutgoingCategoryMaxServoDirectionValue,
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

	// Search for the given outgoing category name
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