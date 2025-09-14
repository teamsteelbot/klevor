package usbcdc

import (
	tinygotypes "github.com/ralvarezdev/tinygo-types"
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
	IncomingCategoryGetMaxMotorSpeedValue
	IncomingCategoryServoDirectionCenter
	IncomingCategoryServoDirectionToLeft
	IncomingCategoryServoDirectionToRight
	IncomingCategoryGetMaxServoDirectionValue
)

// IsAServoCategory checks if the given IncomingCategory is a servo category
//
// Returns:
//
// True if the category is a servo category, otherwise False
func (i IncomingCategory) IsAServoCategory() bool {
	return i == IncomingCategoryServoDirectionCenter ||
		i == IncomingCategoryServoDirectionToLeft ||
		i == IncomingCategoryServoDirectionToRight
}

// IsAMotorCategory checks if the given IncomingCategory is a motor category
//
// Returns:
//
// True if the category is a motor category, otherwise False
func (i IncomingCategory) IsAMotorCategory() bool {
	return i == IncomingCategoryMotorSpeedStop ||
		i == IncomingCategoryMotorSpeedForward ||
		i == IncomingCategoryMotorSpeedBackward
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
func IncomingCategoryFromUint8(value uint8) (IncomingCategory, tinygotypes.ErrorCode) {
	switch IncomingCategory(value) {
	case IncomingCategoryNil:
		return IncomingCategoryNil, tinygotypes.ErrorCodeNil
	case IncomingCategoryStatus:
		return IncomingCategoryStatus, tinygotypes.ErrorCodeNil
	case IncomingCategoryMotorSpeedStop:
		return IncomingCategoryMotorSpeedStop, tinygotypes.ErrorCodeNil
	case IncomingCategoryMotorSpeedForward:
		return IncomingCategoryMotorSpeedForward, tinygotypes.ErrorCodeNil
	case IncomingCategoryMotorSpeedBackward:
		return IncomingCategoryMotorSpeedBackward, tinygotypes.ErrorCodeNil
	case IncomingCategoryGetMaxMotorSpeedValue:
		return IncomingCategoryGetMaxMotorSpeedValue, tinygotypes.ErrorCodeNil
	case IncomingCategoryServoDirectionCenter:
		return IncomingCategoryServoDirectionCenter, tinygotypes.ErrorCodeNil
	case IncomingCategoryServoDirectionToLeft:
		return IncomingCategoryServoDirectionToLeft, tinygotypes.ErrorCodeNil
	case IncomingCategoryServoDirectionToRight:
		return IncomingCategoryServoDirectionToRight, tinygotypes.ErrorCodeNil
	case IncomingCategoryGetMaxServoDirectionValue:
		return IncomingCategoryGetMaxServoDirectionValue, tinygotypes.ErrorCodeNil
	default:
		return IncomingCategoryNil, ErrorCodeUSBCDCUnknownIncomingCategory
	}
}
