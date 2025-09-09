package usbcdc

import (
	tinygotypes "github.com/ralvarezdev/tinygo-types"
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
	OutgoingCategoryDebug
	OutgoingCategoryMaxMotorSpeedValue
	OutgoingCategoryMaxServoDirectionValue
	OutgoingCategoryQuaternionX
	OutgoingCategoryQuaternionY
	OutgoingCategoryQuaternionZ
	OutgoingCategoryQuaternionW
)

// OutgoingCategoryFromUint8 returns the OutgoingCategory enum based on a given uint8 value
//
// Parameters:
//
// value: The uint8 value to search on OutgoingCategories
//
// Returns:
//
// The OutgoingCategory enum value, or an error if the key wasn't found for the given value
func OutgoingCategoryFromUint8(value uint8) (OutgoingCategory, tinygotypes.ErrorCode) {
	switch OutgoingCategory(value) {
	case OutgoingCategoryNil:
		return OutgoingCategoryNil, tinygotypes.ErrorCodeNil
	case OutgoingCategoryChallenge:
		return OutgoingCategoryChallenge, tinygotypes.ErrorCodeNil
	case OutgoingCategoryStatus:
		return OutgoingCategoryStatus, tinygotypes.ErrorCodeNil
	case OutgoingCategoryQuaternionX:
		return OutgoingCategoryQuaternionX, tinygotypes.ErrorCodeNil
	case OutgoingCategoryQuaternionY:
		return OutgoingCategoryQuaternionY, tinygotypes.ErrorCodeNil
	case OutgoingCategoryQuaternionZ:
		return OutgoingCategoryQuaternionZ, tinygotypes.ErrorCodeNil
	case OutgoingCategoryQuaternionW:
		return OutgoingCategoryQuaternionW, tinygotypes.ErrorCodeNil
	case OutgoingCategoryError:
		return OutgoingCategoryError, tinygotypes.ErrorCodeNil
	case OutgoingCategoryDebug:
		return OutgoingCategoryDebug, tinygotypes.ErrorCodeNil
	case OutgoingCategoryMaxMotorSpeedValue:
		return OutgoingCategoryMaxMotorSpeedValue, tinygotypes.ErrorCodeNil
	case OutgoingCategoryMaxServoDirectionValue:
		return OutgoingCategoryMaxServoDirectionValue, tinygotypes.ErrorCodeNil
	default:
		return OutgoingCategoryNil, ErrorCodeUSBCDCInvalidOutgoingCategoryUint8
	}		
}