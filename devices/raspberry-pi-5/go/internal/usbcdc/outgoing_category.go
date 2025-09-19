package usbcdc

import (
	"fmt"
)

type (
	// OutgoingCategory represents the enum categories of outgoing messages from the Raspberry Pi 5
	OutgoingCategory uint8
)

const (
	OutgoingCategoryNil OutgoingCategory = iota
	OutgoingCategoryStatus
	OutgoingCategoryMotorSpeedStop
	OutgoingCategoryMotorSpeedForward
	OutgoingCategoryMotorSpeedBackward
	OutgoingCategoryGetMaxMotorSpeedValue
	OutgoingCategoryServoAngleCenter
	OutgoingCategoryServoAngleToLeft
	OutgoingCategoryServoAngleToRight
	OutgoingCategoryGetMaxServoAngleValue
)

var (
	// OutgoingCategoryNames maps a given OutgoingCategory to its string name
	OutgoingCategoryNames = map[OutgoingCategory]string{
		OutgoingCategoryStatus:                "status",
		OutgoingCategoryMotorSpeedStop:        "motor_speed_stop",
		OutgoingCategoryMotorSpeedForward:     "motor_speed_forward",
		OutgoingCategoryMotorSpeedBackward:    "motor_speed_backward",
		OutgoingCategoryGetMaxMotorSpeedValue: "get_max_motor_speed_value",
		OutgoingCategoryServoAngleCenter:      "servo_angle_center",
		OutgoingCategoryServoAngleToLeft:      "servo_angle_to_left",
		OutgoingCategoryServoAngleToRight:     "servo_angle_to_right",
		OutgoingCategoryGetMaxServoAngleValue: "get_max_servo_angle_value",
	}

	// OutgoingCategories maps a given uint8 value to its OutgoingCategory enum
	OutgoingCategories = map[uint8]OutgoingCategory{
		uint8(OutgoingCategoryNil):                   OutgoingCategoryNil,
		uint8(OutgoingCategoryStatus):                OutgoingCategoryStatus,
		uint8(OutgoingCategoryMotorSpeedStop):        OutgoingCategoryMotorSpeedStop,
		uint8(OutgoingCategoryMotorSpeedForward):     OutgoingCategoryMotorSpeedForward,
		uint8(OutgoingCategoryMotorSpeedBackward):    OutgoingCategoryMotorSpeedBackward,
		uint8(OutgoingCategoryGetMaxMotorSpeedValue): OutgoingCategoryGetMaxMotorSpeedValue,
		uint8(OutgoingCategoryServoAngleCenter):      OutgoingCategoryServoAngleCenter,
		uint8(OutgoingCategoryServoAngleToLeft):      OutgoingCategoryServoAngleToLeft,
		uint8(OutgoingCategoryServoAngleToRight):     OutgoingCategoryServoAngleToRight,
		uint8(OutgoingCategoryGetMaxServoAngleValue): OutgoingCategoryGetMaxServoAngleValue,
	}

	// OutgoingCategoryDataLengths maps a given OutgoingCategory to its data length in bytes
	OutgoingCategoryDataLengths = map[OutgoingCategory]int{
		OutgoingCategoryNil:                   0,
		OutgoingCategoryStatus:                1,
		OutgoingCategoryMotorSpeedStop:        0,
		OutgoingCategoryMotorSpeedForward:     2,
		OutgoingCategoryMotorSpeedBackward:    2,
		OutgoingCategoryGetMaxMotorSpeedValue: 0,
		OutgoingCategoryServoAngleCenter:      0,
		OutgoingCategoryServoAngleToLeft:      2,
		OutgoingCategoryServoAngleToRight:     2,
		OutgoingCategoryGetMaxServoAngleValue: 0,
	}
)

// String returns the name of the OutgoingCategory
//
// Returns:
//
// The name of the OutgoingCategory enum
func (o OutgoingCategory) String() string {
	return OutgoingCategoryNames[o]
}

// Bytes returns the byte slice representation of the OutgoingCategory
//
// Returns:
//
// The byte slice representation of the OutgoingCategory enum
func (o OutgoingCategory) Bytes() []byte {
	return []byte{uint8(o)}
}

// DataLength returns the size in bytes of the data for a given OutgoingCategory
//
// Returns:
//
// The size in bytes of the data for the given category, or an error if the category is invalid
func (o OutgoingCategory) DataLength() (int, error) {
	length, ok := OutgoingCategoryDataLengths[o]
	if !ok {
		return 0, fmt.Errorf(ErrUnknownOutgoingCategory, o)
	}
	return length, nil
}

// IsAServoCategory checks if the given OutgoingCategory is a servo category
//
// Returns:
//
// True if the category is a servo category, otherwise False
func (o OutgoingCategory) IsAServoCategory() bool {
	return o == OutgoingCategoryServoAngleCenter ||
		o == OutgoingCategoryServoAngleToLeft ||
		o == OutgoingCategoryServoAngleToRight
}

// IsAMotorCategory checks if the given OutgoingCategory is a motor category
//
// Returns:
//
// True if the category is a motor category, otherwise False
func (o OutgoingCategory) IsAMotorCategory() bool {
	return o == OutgoingCategoryMotorSpeedStop ||
		o == OutgoingCategoryMotorSpeedForward ||
		o == OutgoingCategoryMotorSpeedBackward
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
		return OutgoingCategoryNil, fmt.Errorf(
			ErrUnknownOutgoingCategory,
			value,
		)
	}
	return category, nil
}

// OutgoingCategoryFromBytes returns the OutgoingCategory enum based on a given byte slice
//
// Parameters:
//
// data: The byte slice to parse as OutgoingCategory
//
// Returns:
//
// The OutgoingCategory enum value, or an error if the key wasn't found for the given value
func OutgoingCategoryFromBytes(data []byte) (OutgoingCategory, error) {
	if len(data) == 0 {
		return OutgoingCategoryNil, ErrNilOutgoingCategory
	}
	return OutgoingCategoryFromUint8(data[0])
}
