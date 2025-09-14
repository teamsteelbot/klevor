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
	OutgoingCategoryMaxMotorSpeedValue
	OutgoingCategoryMaxServoDirectionValue
	OutgoingCategoryQuaternionX
	OutgoingCategoryQuaternionY
	OutgoingCategoryQuaternionZ
	OutgoingCategoryQuaternionW
	OutgoingCategoryEulerDegreesYaw
	OutgoingCategoryEulerDegreesPitch
	OutgoingCategoryEulerDegreesRoll
)

// OutgoingCategoryDataLength returns the size in bytes of the data for a given OutgoingCategory
//
// Parameters:
//
// category: The OutgoingCategory to get the data size for
//
// Returns:
//
// The size in bytes of the data for the given category, or an error if the category is invalid
func OutgoingCategoryDataLength(category OutgoingCategory) (int, tinygotypes.ErrorCode) {
	switch category {
	case OutgoingCategoryNil:
		return 0, ErrorCodeUSBCDCNilOutgoingCategory
	case OutgoingCategoryStatus, OutgoingCategoryChallenge:
		return 1, tinygotypes.ErrorCodeNil
	case OutgoingCategoryError, OutgoingCategoryMaxMotorSpeedValue, OutgoingCategoryMaxServoDirectionValue:
		return 2, tinygotypes.ErrorCodeNil
	case OutgoingCategoryQuaternionX, OutgoingCategoryQuaternionY, OutgoingCategoryQuaternionZ, OutgoingCategoryQuaternionW, OutgoingCategoryEulerDegreesYaw, OutgoingCategoryEulerDegreesPitch, OutgoingCategoryEulerDegreesRoll:
		return 8, tinygotypes.ErrorCodeNil
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
func OutgoingCategoryFromUint8(value uint8) (OutgoingCategory, tinygotypes.ErrorCode) {
	switch OutgoingCategory(value) {
	case OutgoingCategoryNil:
		return OutgoingCategoryNil, tinygotypes.ErrorCodeNil
	case OutgoingCategoryStatus:
		return OutgoingCategoryStatus, tinygotypes.ErrorCodeNil
	case OutgoingCategoryChallenge:
		return OutgoingCategoryChallenge, tinygotypes.ErrorCodeNil
	case OutgoingCategoryError:
		return OutgoingCategoryError, tinygotypes.ErrorCodeNil
	case OutgoingCategoryMaxMotorSpeedValue:
		return OutgoingCategoryMaxMotorSpeedValue, tinygotypes.ErrorCodeNil
	case OutgoingCategoryMaxServoDirectionValue:
		return OutgoingCategoryMaxServoDirectionValue, tinygotypes.ErrorCodeNil
	case OutgoingCategoryQuaternionX:
		return OutgoingCategoryQuaternionX, tinygotypes.ErrorCodeNil
	case OutgoingCategoryQuaternionY:
		return OutgoingCategoryQuaternionY, tinygotypes.ErrorCodeNil
	case OutgoingCategoryQuaternionZ:
		return OutgoingCategoryQuaternionZ, tinygotypes.ErrorCodeNil
	case OutgoingCategoryQuaternionW:
		return OutgoingCategoryQuaternionW, tinygotypes.ErrorCodeNil
	case OutgoingCategoryEulerDegreesYaw:
		return OutgoingCategoryEulerDegreesYaw, tinygotypes.ErrorCodeNil
	case OutgoingCategoryEulerDegreesPitch:
		return OutgoingCategoryEulerDegreesPitch, tinygotypes.ErrorCodeNil
	case OutgoingCategoryEulerDegreesRoll:
		return OutgoingCategoryEulerDegreesRoll, tinygotypes.ErrorCodeNil
	default:
		return OutgoingCategoryNil, ErrorCodeUSBCDCUnknownOutgoingCategory
	}		
}