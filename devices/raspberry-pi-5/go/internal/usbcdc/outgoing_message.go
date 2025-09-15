package usbcdc

import (
	"bytes"
	"fmt"
)

type (
	// OutgoingMessage is the struct to handle the messages sent to the Raspberry Pi 5
	OutgoingMessage struct {
		Category OutgoingCategory
		Data     []byte
	}
)

// NewOutgoingMessage creates a new instance of OutgoingMessage
//
// Parameters:
//
// category: The category of the message
// data: The data of the message
//
// Returns:
//
// An instance of OutgoingMessage
func NewOutgoingMessage(
	category OutgoingCategory,
	data []byte,
) *OutgoingMessage {
	return &OutgoingMessage{
		Category: category,
		Data:     data,
	}
}

// NewOutgoingMessageFromUint8Data creates a new instance of OutgoingMessage with uint8 data
//
// Parameters:
//
// category: The category of the message
// data: The uint8 data of the message
//
// Returns:
//
// An instance of OutgoingMessage
func NewOutgoingMessageFromUint8Data(
	category OutgoingCategory,
	data uint8,
) *OutgoingMessage {
	return &OutgoingMessage{
		Category: category,
		Data:     []byte{data},
	}
}

// NewOutgoingStatusMessage creates a new instance of OutgoingMessage with status data
//
// Parameters:
//
// status: The status data of the message
//
// Returns:
//
// An instance of OutgoingMessage
func NewOutgoingStatusMessage(
	status OutgoingStatus,
) *OutgoingMessage {
	return NewOutgoingMessageFromUint8Data(
		OutgoingCategoryStatus,
		uint8(status),
	)
}

// NewOutgoingMessageFromUint16Data creates a new instance of OutgoingMessage with uint16 data
//
// Parameters:
//
// category: The category of the message
// data: The uint16 data of the message
//
// Returns:
//
// An instance of OutgoingMessage
func NewOutgoingMessageFromUint16Data(
	category OutgoingCategory,
	data uint16,
) *OutgoingMessage {
	return &OutgoingMessage{
		Category: category,
		Data:     []byte{uint8(data >> 8), uint8(data & 0xFF)},
	}
}

// StringToPrint returns a human-readable string representation of the OutgoingMessage
//
// Returns:
//
// A human-readable string that represents the OutgoingMessage
func (msg *OutgoingMessage) StringToPrint() string {
	switch msg.Category {
	case OutgoingCategoryMotorSpeedStop,
		OutgoingCategoryServoDirectionCenter,
		OutgoingCategoryGetMaxMotorSpeedValue,
		OutgoingCategoryGetMaxServoDirectionValue:
		return fmt.Sprintf(
			"OutgoingMessage{Category: %s, Data: <no content>}",
			msg.Category.String(),
		)
	case OutgoingCategoryMotorSpeedForward,
		OutgoingCategoryMotorSpeedBackward,
		OutgoingCategoryServoDirectionToLeft,
		OutgoingCategoryServoDirectionToRight:
		if len(msg.Data) != 2 {
			return fmt.Sprintf(
				"OutgoingMessage{Category: %s, Data: %q (invalid length: %d, expected 2)}",
				msg.Category.String(),
				msg.Data,
				len(msg.Data),
			)
		}

		// Combine the two bytes into a uint16 value
		value := (uint16(msg.Data[0]) << 8) | uint16(msg.Data[1])
		return fmt.Sprintf(
			"OutgoingMessage{Category: %s, Data: %q (%d)}",
			msg.Category.String(),
			msg.Data,
			value,
		)
	case OutgoingCategoryStatus:
		outgoingStatus, err := OutgoingStatusFromBytes(msg.Data)
		if err != nil {
			return fmt.Sprintf(
				"OutgoingMessage{Category: %s, Data: %q (invalid status: %v)}",
				msg.Category.String(),
				msg.Data,
				err,
			)
		}
		if outgoingStatus != OutgoingStatusNil {
			return fmt.Sprintf(
				"OutgoingMessage{Category: %s, Data: %q (%s)}",
				msg.Category.String(),
				msg.Data,
				outgoingStatus.String(),
			)
		}
		fallthrough
	default:
		return fmt.Sprintf(
			"OutgoingMessage{Category: %s, Data: %q}",
			msg.Category.String(),
			msg.Data,
		)
	}
}

// IsEqual compares the given instance of OutgoingMessage with the current one
//
// Parameters:
//
// other: Pointer to the instance of OutgoingMessage to be compared
//
// Returns:
//
// True if they're equal, otherwise False
func (msg *OutgoingMessage) IsEqual(other *OutgoingMessage) bool {
	// Check if the instance to be compared is nil
	if other == nil {
		return false
	}
	return msg.Category == other.Category && bytes.Equal(msg.Data, other.Data)
}

// IsAServoMessage checks if the OutgoingMessage is a servo-related message
//
// Returns:
//
// True if the message is related to servo operations, otherwise False
func (msg *OutgoingMessage) IsAServoMessage() bool {
	return msg.Category.IsAServoCategory()
}

// IsAMotorMessage checks if the OutgoingMessage is a motor-related message
//
// Returns:
//
// True if the message is related to motor operations, otherwise False
func (msg *OutgoingMessage) IsAMotorMessage() bool {
	return msg.Category.IsAMotorCategory()
}
