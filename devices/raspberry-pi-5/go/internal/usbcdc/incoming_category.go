package usbcdc

import (
	"fmt"
)

type (
	// IncomingCategory represents the enum categories of incoming messages to the Raspberry Pi 5
	IncomingCategory uint8
)

const (
	IncomingCategoryNil IncomingCategory = iota
	IncomingCategoryChallenge
	IncomingCategoryStatus
	IncomingCategoryError
	IncomingCategoryQuaternionX
	IncomingCategoryQuaternionY
	IncomingCategoryQuaternionZ
	IncomingCategoryQuaternionW
	IncomingCategoryEulerDegreesYaw
	IncomingCategoryEulerDegreesPitch
	IncomingCategoryEulerDegreesRoll
	IncomingCategoryMotorSpeedStart
	IncomingCategoryMotorSpeedEnd
	IncomingCategoryServoAngleStart
	IncomingCategoryServoAngleEnd
)

var (
	// IncomingCategoryNames maps a given IncomingCategory to its string name
	IncomingCategoryNames = map[IncomingCategory]string{
		IncomingCategoryChallenge:         "challenge",
		IncomingCategoryStatus:            "status",
		IncomingCategoryError:             "error",
		IncomingCategoryQuaternionX:       "quaternion_x",
		IncomingCategoryQuaternionY:       "quaternion_y",
		IncomingCategoryQuaternionZ:       "quaternion_z",
		IncomingCategoryQuaternionW:       "quaternion_w",
		IncomingCategoryEulerDegreesYaw:   "euler_degrees_yaw",
		IncomingCategoryEulerDegreesPitch: "euler_degrees_pitch",
		IncomingCategoryEulerDegreesRoll:  "euler_degrees_roll",
		IncomingCategoryMotorSpeedStart:   "motor_speed_start",
		IncomingCategoryMotorSpeedEnd:     "motor_speed_end",
		IncomingCategoryServoAngleStart:   "servo_angle_start",
		IncomingCategoryServoAngleEnd:     "servo_angle_end",
	}

	// IncomingCategories maps a given uint8 value to its IncomingCategory enum
	IncomingCategories = map[uint8]IncomingCategory{
		uint8(IncomingCategoryNil):               IncomingCategoryNil,
		uint8(IncomingCategoryChallenge):         IncomingCategoryChallenge,
		uint8(IncomingCategoryStatus):            IncomingCategoryStatus,
		uint8(IncomingCategoryError):             IncomingCategoryError,
		uint8(IncomingCategoryQuaternionX):       IncomingCategoryQuaternionX,
		uint8(IncomingCategoryQuaternionY):       IncomingCategoryQuaternionY,
		uint8(IncomingCategoryQuaternionZ):       IncomingCategoryQuaternionZ,
		uint8(IncomingCategoryQuaternionW):       IncomingCategoryQuaternionW,
		uint8(IncomingCategoryEulerDegreesYaw):   IncomingCategoryEulerDegreesYaw,
		uint8(IncomingCategoryEulerDegreesPitch): IncomingCategoryEulerDegreesPitch,
		uint8(IncomingCategoryEulerDegreesRoll):  IncomingCategoryEulerDegreesRoll,
		uint8(IncomingCategoryMotorSpeedStart):   IncomingCategoryMotorSpeedStart,
		uint8(IncomingCategoryMotorSpeedEnd):     IncomingCategoryMotorSpeedEnd,
		uint8(IncomingCategoryServoAngleStart):   IncomingCategoryServoAngleStart,
		uint8(IncomingCategoryServoAngleEnd):     IncomingCategoryServoAngleEnd,
	}

	// IncomingCategoryDataLengths maps a given IncomingCategory to its data length in bytes
	IncomingCategoryDataLengths = map[IncomingCategory]int{
		IncomingCategoryNil:               0,
		IncomingCategoryChallenge:         1,
		IncomingCategoryStatus:            1,
		IncomingCategoryError:             2,
		IncomingCategoryQuaternionX:       8,
		IncomingCategoryQuaternionY:       8,
		IncomingCategoryQuaternionZ:       8,
		IncomingCategoryQuaternionW:       8,
		IncomingCategoryEulerDegreesYaw:   8,
		IncomingCategoryEulerDegreesPitch: 8,
		IncomingCategoryEulerDegreesRoll:  8,
		IncomingCategoryMotorSpeedStart:   0,
		IncomingCategoryMotorSpeedEnd:     0,
		IncomingCategoryServoAngleStart:   0,
		IncomingCategoryServoAngleEnd:     0,
	}
)

// String returns the name of the IncomingCategory
//
// Returns:
//
// The name of the IncomingCategory enum
func (i IncomingCategory) String() string {
	return IncomingCategoryNames[i]
}

// Bytes returns the byte slice representation of the IncomingCategory
//
// Returns:
//
// The byte slice representation of the IncomingCategory enum
func (i IncomingCategory) Bytes() []byte {
	return []byte{uint8(i)}
}

// DataLength returns the size in bytes of the data for a given IncomingCategory
//
// Returns:
//
// The size in bytes of the data for the given category, or an error if the category is invalid
func (i IncomingCategory) DataLength() (int, error) {
	length, ok := IncomingCategoryDataLengths[i]
	if !ok {
		return 0, fmt.Errorf(ErrUnknownIncomingCategory, i)
	}
	return length, nil
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
		return IncomingCategoryNil, fmt.Errorf(
			ErrUnknownIncomingCategory,
			value,
		)
	}
	return category, nil
}

// IncomingCategoryFromBytes returns the IncomingCategory enum based on a given byte slice
//
// Parameters:
//
// data: The byte slice to parse as IncomingCategory
//
// Returns:
//
// The IncomingCategory enum value, or an error if the key wasn't found for the given value
func IncomingCategoryFromBytes(data []byte) (IncomingCategory, error) {
	if len(data) == 0 {
		return IncomingCategoryNil, ErrNilIncomingCategory
	}
	return IncomingCategoryFromUint8(data[0])
}
