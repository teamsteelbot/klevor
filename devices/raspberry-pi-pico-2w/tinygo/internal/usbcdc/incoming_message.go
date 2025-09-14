package usbcdc

import (
	tinygotypes "github.com/ralvarezdev/tinygo-types"
)

type (
	// IncomingMessage is the struct to handle the buffers received to the Raspberry Pi 5
	IncomingMessage struct {
		Category IncomingCategory
		Data     []byte
	}
)

// NewIncomingMessage creates a new instance of IncomingMessage
//
// Parameters:
//
// category: The category of the incoming message
// data: The data buffer of the incoming message
//
// Returns:
//
// An instance of IncomingMessage
func NewIncomingMessage(
	category IncomingCategory,
	data []byte,
) IncomingMessage {
	return IncomingMessage{
		Category: category,
		Data:     data,
	}
}

// NewIncomingMessageFromBuffer creates a new instance of IncomingMessage
//
// Parameters:
//
// buffer: The byte slice buffer containing the incoming buffer
//
// Returns:
//
// An instance of IncomingMessage
func NewIncomingMessageFromBuffer(
	buffer []byte,
) (IncomingMessage, tinygotypes.ErrorCode) {
	// Check if the buffer is nil
	if buffer == nil {
		return IncomingMessage{}, ErrorCodeUSBCDCNilIncomingMessageBuffer
	}

	// Get the index of the end character and copy the buffer until that index
	endIdx := -1
	for i, b := range buffer {
		if b == EndChar {
			endIdx = i
			break
		}
	}
	if endIdx == -1 {
		return nil, ErrorCodeUSBCDCInvalidIncomingMessageMissingEndCharacter
	}

	// Create a copy of the buffer up to the end character
	bufferCopy := make([]byte, endIdx)
	copy(bufferCopy, buffer[:endIdx])

	// Check if the buffer is empty
	if len(bufferCopy) == 0 {
		return nil, ErrorCodeUSBCDCEmptyIncomingMessageBuffer
	}

	// Convert the category to a Category enum value
	category, err := IncomingCategoryFromUint8(buffer[0])
	if err != tinygotypes.ErrorCodeNil {
		return nil, err
	}

	// Check if based on the incoming category the buffer content can be empty or not
	if category == IncomingCategoryMotorSpeedStop ||
		category == IncomingCategoryServoDirectionCenter ||
		category == IncomingCategoryGetMaxMotorSpeedValue ||
		category == IncomingCategoryGetMaxServoDirectionValue {
		return &IncomingMessage{
			Category: category,
			Buffer:  bufferCopy,
		}, tinygotypes.ErrorCodeNil
	}

	// Check if the buffer has content
	if len(bufferCopy) == 1 {
		return nil, ErrorCodeUSBCDCIncomingMessageEmptyContent
	}

	// Create and return the IncomingMessage object
	return &IncomingMessage{
		Category: category,
		Buffer:   bufferCopy,
	}, tinygotypes.ErrorCodeNil
}

// NewIncomingStatusMessage creates a new instance of IncomingMessage for status messages
//
// Parameters:
//
// status: The status to be converted into an IncomingMessage
//
// Returns:
//
// An instance of IncomingMessage
func NewIncomingStatusMessage(status IncomingStatus) *IncomingMessage {
	i, _ := NewIncomingMessageFromBuffer([]byte{uint8(IncomingCategoryStatus), uint8(status), EndChar})
	return i
}

// IsEqual compares the given instance of IncomingMessage with the current one
//
// Parameters:
//
// other: Pointer to the instance of IncomingMessage to be compared
//
// Returns:
//
// True if they're equal, otherwise False
func (i *IncomingMessage) IsEqual(other *IncomingMessage) bool {
	// Check if the instance to be compared is nil
	if other == nil {
		return false
	}

	// Compare the buffers
	if len(i.Buffer) != len(other.Buffer) {
		return false
	}
	for idx := range i.Buffer {
		if i.Buffer[idx] != other.Buffer[idx] {
			return false
		}
	}
	return true
}

// IsAServoMessage checks if the IncomingMessage is a servo-related buffer
//
// Returns:
//
// True if the buffer is related to servo operations, otherwise False
func (i *IncomingMessage) IsAServoMessage() bool {
	return i.Category.IsAServoCategory()
}

// IsAMotorMessage checks if the IncomingMessage is a motor-related buffer
//
// Returns:
//
// True if the buffer is related to motor operations, otherwise False
func (i *IncomingMessage) IsAMotorMessage() bool {
	return i.Category.IsAMotorCategory()
}

// GetContentBuffer returns the content buffer of the IncomingMessage
//
// Returns:
//
// A byte slice representing the content buffer, excluding the category byte.
func (i *IncomingMessage) GetContentBuffer() []byte {
	return i.Buffer[1:]
}

// GetContentAsUint16 converts the buffer of the IncomingMessage to a uint16 value
//
// Returns:
//
// The uint16 representation of the buffer, or an error if the conversion fails
func (i *IncomingMessage) GetContentAsUint16() (uint16, tinygotypes.ErrorCode) {
	buf := i.GetContentBuffer()
    var val uint16
    for _, b := range buf {
        if b < '0' || b > '9' {
            return 0, ErrorCodeUSBCDCInvalidIncomingMessageContentUint16
        }
        val = val*10 + uint16(b-'0')
    }
    return val, tinygotypes.ErrorCodeNil
}
