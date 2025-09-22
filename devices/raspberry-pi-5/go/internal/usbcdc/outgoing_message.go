package usbcdc

import (
	"bytes"
	"encoding/binary"
	"fmt"
	"math"
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
	buffer := make([]byte, 2)
	binary.BigEndian.PutUint16(buffer, data)
	return &OutgoingMessage{
		Category: category,
		Data:     buffer,
	}
}

// NewOutgoingMessageFromFloat64Data creates a new instance of OutgoingMessage with float64 data
//
// Parameters:
//
// category: The category of the message
// data: The float64 data of the message
//
// Returns:
//
// An instance of OutgoingMessage
func NewOutgoingMessageFromFloat64Data(
	category OutgoingCategory,
	data float64,
) *OutgoingMessage {
	buffer := make([]byte, 8)
	bits := math.Float64bits(data)
	binary.BigEndian.PutUint64(buffer, bits)
	return &OutgoingMessage{
		Category: category,
		Data:     buffer,
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

// StringToPrint returns a human-readable string representation of the OutgoingMessage
//
// Returns:
//
// A human-readable string that represents the OutgoingMessage
func (msg *OutgoingMessage) StringToPrint() string {
	var dataDetails string

	switch msg.Category {
	case OutgoingCategoryMotorSpeedStop,
		OutgoingCategoryServoAngleCenter:
		dataDetails = "<no content>"
	case OutgoingCategoryMotorSpeedForward,
		OutgoingCategoryMotorSpeedBackward,
		OutgoingCategoryServoAngleToLeft,
		OutgoingCategoryServoAngleToRight:
		if len(msg.Data) != 8 {
			dataDetails = fmt.Sprintf(
				"invalid length: %d, expected: 8",
				len(msg.Data),
			)
			break
		}

		// Combine the eight bytes to float 64 value
		bits := binary.BigEndian.Uint64(msg.Data[:])
		value := math.Float64frombits(bits)
		dataDetails = fmt.Sprintf("%f", value)
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
