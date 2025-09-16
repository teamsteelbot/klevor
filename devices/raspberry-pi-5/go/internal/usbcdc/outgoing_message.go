package usbcdc

import (
	"bytes"
	"fmt"
	"encoding/binary"
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
	var dataDetails string

	switch msg.Category {
	case OutgoingCategoryMotorSpeedStop,
		OutgoingCategoryServoDirectionCenter,
		OutgoingCategoryGetMaxMotorSpeedValue,
		OutgoingCategoryGetMaxServoDirectionValue:
		dataDetails = "<no content>"
	case OutgoingCategoryMotorSpeedForward,
		OutgoingCategoryMotorSpeedBackward,
		OutgoingCategoryServoDirectionToLeft,
		OutgoingCategoryServoDirectionToRight:
		if len(msg.Data) != 2 {
			dataDetails = fmt.Sprintf("invalid length: %d, expected: 2", len(msg.Data))
			break
		}

		// Combine the two bytes into a uint16 value
		value := binary.BigEndian.Uint16(msg.Data[:])
		dataDetails = fmt.Sprintf("%d", value)
	case OutgoingCategoryStatus:
		outgoingStatus, err := OutgoingStatusFromBytes(msg.Data)
		if err != nil {
			dataDetails = fmt.Sprintf("invalid status: %v", err)
			break
		}
		if outgoingStatus != OutgoingStatusNil {
			dataDetails = outgoingStatus.String()
			break
		}
		dataDetails = "nil status"
	}

	// Check if there are no details for the data
	if dataDetails == "" {
		return fmt.Sprintf(
			"OutgoingMessage{Category: [0x%02X] (%s), Data: [%s]}",
			uint8(msg.Category),
			msg.Category.String(),
			ConvertBytesSliceToHexString(msg.Data),
		)
	}

	// Return the formatted string with details
	return fmt.Sprintf(
		"OutgoingMessage{Category: [0x%02X] (%s), Data: [%s] (%s)}",
		uint8(msg.Category),
		msg.Category.String(),
		ConvertBytesSliceToHexString(msg.Data),
		dataDetails,
	)
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
