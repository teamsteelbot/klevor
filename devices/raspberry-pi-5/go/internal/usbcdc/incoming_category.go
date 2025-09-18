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
	IncomingCategoryMaxMotorSpeedValue
	IncomingCategoryMaxServoDirectionValue
	IncomingCategoryQuaternionX
	IncomingCategoryQuaternionY
	IncomingCategoryQuaternionZ
	IncomingCategoryQuaternionW
	IncomingCategoryEulerDegreesYaw
	IncomingCategoryEulerDegreesPitch
	IncomingCategoryEulerDegreesRoll
	IncomingCategorySetMotorSpeedStop
	IncomingCategorySetMotorSpeedForward
	IncomingCategorySetMotorSpeedBackward
	IncomingCategorySetServoDirectionCenter
	IncomingCategorySetServoDirectionToLeft
	IncomingCategorySetServoDirectionToRight
)

var (
	// IncomingCategoryNames maps a given IncomingCategory to its string name
	IncomingCategoryNames = map[IncomingCategory]string{
		IncomingCategoryChallenge:                "challenge",
		IncomingCategoryStatus:                   "status",
		IncomingCategoryError:                    "error",
		IncomingCategoryMaxMotorSpeedValue:       "max_motor_speed_value",
		IncomingCategoryMaxServoDirectionValue:   "max_servo_direction_value",
		IncomingCategoryQuaternionX:              "quaternion_x",
		IncomingCategoryQuaternionY:              "quaternion_y",
		IncomingCategoryQuaternionZ:              "quaternion_z",
		IncomingCategoryQuaternionW:              "quaternion_w",
		IncomingCategoryEulerDegreesYaw:          "euler_degrees_yaw",
		IncomingCategoryEulerDegreesPitch:        "euler_degrees_pitch",
		IncomingCategoryEulerDegreesRoll:         "euler_degrees_roll",
		IncomingCategorySetMotorSpeedStop:        "set_motor_speed_stop",
		IncomingCategorySetMotorSpeedForward:     "set_motor_speed_forward",
		IncomingCategorySetMotorSpeedBackward:    "set_motor_speed_backward",
		IncomingCategorySetServoDirectionCenter:  "set_servo_direction_center",
		IncomingCategorySetServoDirectionToLeft:  "set_servo_direction_to_left",
		IncomingCategorySetServoDirectionToRight: "set_servo_direction_to_right",
	}

	// IncomingCategories maps a given uint8 value to its IncomingCategory enum
	IncomingCategories = map[uint8]IncomingCategory{
		uint8(IncomingCategoryNil):                      IncomingCategoryNil,
		uint8(IncomingCategoryChallenge):                IncomingCategoryChallenge,
		uint8(IncomingCategoryStatus):                   IncomingCategoryStatus,
		uint8(IncomingCategoryError):                    IncomingCategoryError,
		uint8(IncomingCategoryMaxMotorSpeedValue):       IncomingCategoryMaxMotorSpeedValue,
		uint8(IncomingCategoryMaxServoDirectionValue):   IncomingCategoryMaxServoDirectionValue,
		uint8(IncomingCategoryQuaternionX):              IncomingCategoryQuaternionX,
		uint8(IncomingCategoryQuaternionY):              IncomingCategoryQuaternionY,
		uint8(IncomingCategoryQuaternionZ):              IncomingCategoryQuaternionZ,
		uint8(IncomingCategoryQuaternionW):              IncomingCategoryQuaternionW,
		uint8(IncomingCategoryEulerDegreesYaw):          IncomingCategoryEulerDegreesYaw,
		uint8(IncomingCategoryEulerDegreesPitch):        IncomingCategoryEulerDegreesPitch,
		uint8(IncomingCategoryEulerDegreesRoll):         IncomingCategoryEulerDegreesRoll,
		uint8(IncomingCategorySetMotorSpeedStop):        IncomingCategorySetMotorSpeedStop,
		uint8(IncomingCategorySetMotorSpeedForward):     IncomingCategorySetMotorSpeedForward,
		uint8(IncomingCategorySetMotorSpeedBackward):    IncomingCategorySetMotorSpeedBackward,
		uint8(IncomingCategorySetServoDirectionCenter):  IncomingCategorySetServoDirectionCenter,
		uint8(IncomingCategorySetServoDirectionToLeft):  IncomingCategorySetServoDirectionToLeft,
		uint8(IncomingCategorySetServoDirectionToRight): IncomingCategorySetServoDirectionToRight,
	}

	// IncomingCategoryDataLengths maps a given IncomingCategory to its data length in bytes
	IncomingCategoryDataLengths = map[IncomingCategory]int{
		IncomingCategoryNil:                      0,
		IncomingCategoryChallenge:                1,
		IncomingCategoryStatus:                   1,
		IncomingCategoryError:                    2,
		IncomingCategoryMaxMotorSpeedValue:       2,
		IncomingCategoryMaxServoDirectionValue:   2,
		IncomingCategoryQuaternionX:              8,
		IncomingCategoryQuaternionY:              8,
		IncomingCategoryQuaternionZ:              8,
		IncomingCategoryQuaternionW:              8,
		IncomingCategoryEulerDegreesYaw:          8,
		IncomingCategoryEulerDegreesPitch:        8,
		IncomingCategoryEulerDegreesRoll:         8,
		IncomingCategorySetMotorSpeedStop:        0,
		IncomingCategorySetMotorSpeedForward:     2,
		IncomingCategorySetMotorSpeedBackward:    2,
		IncomingCategorySetServoDirectionCenter:  0,
		IncomingCategorySetServoDirectionToLeft:  2,
		IncomingCategorySetServoDirectionToRight: 2,
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
