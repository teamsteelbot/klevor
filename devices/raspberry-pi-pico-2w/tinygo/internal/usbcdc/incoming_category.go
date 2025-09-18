package usbcdc

import (
	tinygoerrors "github.com/ralvarezdev/tinygo-errors"
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

// DataLength returns the size in bytes of the data for a given IncomingCategory
//
// Returns:
//
// The size in bytes of the data for the given category, or an error if the category is invalid
func (i IncomingCategory) DataLength() (int, tinygoerrors.ErrorCode) {
	switch i {
	case IncomingCategoryNil:
		return 0, ErrorCodeUSBCDCNilIncomingCategory
	case IncomingCategoryMotorSpeedStop, IncomingCategoryServoDirectionCenter, IncomingCategoryGetMaxMotorSpeedValue, IncomingCategoryGetMaxServoDirectionValue:
		return 0, tinygoerrors.ErrorCodeNil
	case IncomingCategoryStatus:
		return 1, tinygoerrors.ErrorCodeNil
	case IncomingCategoryMotorSpeedForward, IncomingCategoryMotorSpeedBackward, IncomingCategoryServoDirectionToLeft, IncomingCategoryServoDirectionToRight:
		return 2, tinygoerrors.ErrorCodeNil
	default:
		return 0, ErrorCodeUSBCDCUnknownIncomingCategory
	}
}

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
func IncomingCategoryFromUint8(value uint8) (
	IncomingCategory,
	tinygoerrors.ErrorCode,
) {
	switch IncomingCategory(value) {
	case IncomingCategoryNil:
		return IncomingCategoryNil, tinygoerrors.ErrorCodeNil
	case IncomingCategoryStatus:
		return IncomingCategoryStatus, tinygoerrors.ErrorCodeNil
	case IncomingCategoryMotorSpeedStop:
		return IncomingCategoryMotorSpeedStop, tinygoerrors.ErrorCodeNil
	case IncomingCategoryMotorSpeedForward:
		return IncomingCategoryMotorSpeedForward, tinygoerrors.ErrorCodeNil
	case IncomingCategoryMotorSpeedBackward:
		return IncomingCategoryMotorSpeedBackward, tinygoerrors.ErrorCodeNil
	case IncomingCategoryGetMaxMotorSpeedValue:
		return IncomingCategoryGetMaxMotorSpeedValue, tinygoerrors.ErrorCodeNil
	case IncomingCategoryServoDirectionCenter:
		return IncomingCategoryServoDirectionCenter, tinygoerrors.ErrorCodeNil
	case IncomingCategoryServoDirectionToLeft:
		return IncomingCategoryServoDirectionToLeft, tinygoerrors.ErrorCodeNil
	case IncomingCategoryServoDirectionToRight:
		return IncomingCategoryServoDirectionToRight, tinygoerrors.ErrorCodeNil
	case IncomingCategoryGetMaxServoDirectionValue:
		return IncomingCategoryGetMaxServoDirectionValue, tinygoerrors.ErrorCodeNil
	default:
		return IncomingCategoryNil, ErrorCodeUSBCDCUnknownIncomingCategory
	}
}
