package usbcdc

import (
	tinygoerrors "github.com/ralvarezdev/tinygo-errors"
)

type (
	// OutgoingCategory represents the enum categories of outgoing messages to the Raspberry Pi 5
	OutgoingCategory uint8
)

const (
	OutgoingCategoryNil OutgoingCategory = iota
	OutgoingCategoryChallenge
	OutgoingCategoryStatus
	OutgoingCategoryError
	OutgoingCategoryMaxMotorSpeedValue
	OutgoingCategoryMaxServoDirectionValue
	OutgoingCategoryQuaternionX
	OutgoingCategoryQuaternionY
	OutgoingCategoryQuaternionZ
	OutgoingCategoryQuaternionW
	OutgoingCategoryEulerDegreesYaw
	OutgoingCategoryEulerDegreesPitch
	OutgoingCategoryEulerDegreesRoll
	OutgoingCategorySetMotorSpeedStop
	OutgoingCategorySetMotorSpeedForward
	OutgoingCategorySetMotorSpeedBackward
	OutgoingCategorySetServoDirectionCenter
	OutgoingCategorySetServoDirectionToLeft
	OutgoingCategorySetServoDirectionToRight
)

// DataLength returns the size in bytes of the data for a given OutgoingCategory
//
// Returns:
//
// The size in bytes of the data for the given category, or an error if the category is invalid
func (o OutgoingCategory) DataLength() (int, tinygoerrors.ErrorCode) {
	switch o {
	case OutgoingCategoryNil:
		return 0, ErrorCodeUSBCDCNilOutgoingCategory
		case OutgoingCategorySetMotorSpeedStop, OutgoingCategorySetServoDirectionCenter:
		return 0, tinygoerrors.ErrorCodeNil
	case OutgoingCategoryStatus, OutgoingCategoryChallenge:
		return 1, tinygoerrors.ErrorCodeNil
	case OutgoingCategoryError, OutgoingCategoryMaxMotorSpeedValue, OutgoingCategoryMaxServoDirectionValue, OutgoingCategorySetMotorSpeedForward, OutgoingCategorySetMotorSpeedBackward, OutgoingCategorySetServoDirectionToLeft, OutgoingCategorySetServoDirectionToRight:
		return 2, tinygoerrors.ErrorCodeNil
	case OutgoingCategoryQuaternionX, OutgoingCategoryQuaternionY, OutgoingCategoryQuaternionZ, OutgoingCategoryQuaternionW, OutgoingCategoryEulerDegreesYaw, OutgoingCategoryEulerDegreesPitch, OutgoingCategoryEulerDegreesRoll:
		return 8, tinygoerrors.ErrorCodeNil
	default:
		return 0, ErrorCodeUSBCDCUnknownOutgoingCategory
	}
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
func OutgoingCategoryFromUint8(value uint8) (OutgoingCategory, tinygoerrors.ErrorCode) {
	switch OutgoingCategory(value) {
	case OutgoingCategoryNil:
		return OutgoingCategoryNil, tinygoerrors.ErrorCodeNil
	case OutgoingCategoryStatus:
		return OutgoingCategoryStatus, tinygoerrors.ErrorCodeNil
	case OutgoingCategoryChallenge:
		return OutgoingCategoryChallenge, tinygoerrors.ErrorCodeNil
	case OutgoingCategoryError:
		return OutgoingCategoryError, tinygoerrors.ErrorCodeNil
	case OutgoingCategoryMaxMotorSpeedValue:
		return OutgoingCategoryMaxMotorSpeedValue, tinygoerrors.ErrorCodeNil
	case OutgoingCategoryMaxServoDirectionValue:
		return OutgoingCategoryMaxServoDirectionValue, tinygoerrors.ErrorCodeNil
	case OutgoingCategoryQuaternionX:
		return OutgoingCategoryQuaternionX, tinygoerrors.ErrorCodeNil
	case OutgoingCategoryQuaternionY:
		return OutgoingCategoryQuaternionY, tinygoerrors.ErrorCodeNil
	case OutgoingCategoryQuaternionZ:
		return OutgoingCategoryQuaternionZ, tinygoerrors.ErrorCodeNil
	case OutgoingCategoryQuaternionW:
		return OutgoingCategoryQuaternionW, tinygoerrors.ErrorCodeNil
	case OutgoingCategoryEulerDegreesYaw:
		return OutgoingCategoryEulerDegreesYaw, tinygoerrors.ErrorCodeNil
	case OutgoingCategoryEulerDegreesPitch:
		return OutgoingCategoryEulerDegreesPitch, tinygoerrors.ErrorCodeNil
	case OutgoingCategoryEulerDegreesRoll:
		return OutgoingCategoryEulerDegreesRoll, tinygoerrors.ErrorCodeNil
	case OutgoingCategorySetMotorSpeedStop:
		return OutgoingCategorySetMotorSpeedStop, tinygoerrors.ErrorCodeNil
	case OutgoingCategorySetMotorSpeedForward:
		return OutgoingCategorySetMotorSpeedForward, tinygoerrors.ErrorCodeNil
	case OutgoingCategorySetMotorSpeedBackward:
		return OutgoingCategorySetMotorSpeedBackward, tinygoerrors.ErrorCodeNil
	case OutgoingCategorySetServoDirectionCenter:
		return OutgoingCategorySetServoDirectionCenter, tinygoerrors.ErrorCodeNil
	case OutgoingCategorySetServoDirectionToLeft:
		return OutgoingCategorySetServoDirectionToLeft, tinygoerrors.ErrorCodeNil
	case OutgoingCategorySetServoDirectionToRight:
		return OutgoingCategorySetServoDirectionToRight, tinygoerrors.ErrorCodeNil	
	default:
		return OutgoingCategoryNil, ErrorCodeUSBCDCUnknownOutgoingCategory
	}		
}