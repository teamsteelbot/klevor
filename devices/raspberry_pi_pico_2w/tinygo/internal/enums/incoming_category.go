package enums

import (
	"fmt"
	"strings"
)

type (
	// IncomingCategory represent the enum categories of incoming messages from the Raspberry Pi 5
	IncomingCategory int
)

const (
	IncomingCategoryNil IncomingCategory = iota
	IncomingCategoryStatus
	IncomingCategoryMotorSpeed
	IncomingCategoryServoAngle
)

var (
	// IncomingCategoryNames maps a given IncomingCategory to its string name
	IncomingCategoryNames = map[IncomingCategory]string{
		IncomingCategoryStatus:     "status",
		IncomingCategoryMotorSpeed: "motor_speed",
		IncomingCategoryServoAngle: "servo_angle",
	}
)

// String returns the string representation of the IncomingCategory
//
// Returns:
//
// The string representation of the IncomingCategory enum
func (i IncomingCategory) String() string {
	return IncomingCategoryNames[i]
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
