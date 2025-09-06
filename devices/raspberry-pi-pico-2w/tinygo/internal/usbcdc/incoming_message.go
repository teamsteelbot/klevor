package usbcdc

import (
	"fmt"
	"strconv"
	"strings"

	internalusbcdcenums "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/usbcdc/enums"
)

type (
	// IncomingMessage is the struct to handle the messages received to the Raspberry Pi 5
	IncomingMessage struct {
		Category internalusbcdcenums.IncomingCategory
		Content  string
	}
)

// NewIncomingMessage creates a new instance of IncomingMessage
//
// Parameters:
//
// category: The category of the message
// content: The content of the message
//
// Returns:
//
// An instance of IncomingMessage
func NewIncomingMessage(
	category internalusbcdcenums.IncomingCategory,
	content string,
) *IncomingMessage {
	return &IncomingMessage{
		Category: category,
		Content:  strings.TrimSpace(content),
	}
}

// NewIncomingMessageFromUint8Content creates a new instance of IncomingMessage with uint8 content
//
// Parameters:
//
// category: The category of the message
// content: The uint8 content of the message
//
// Returns:
//
// An instance of IncomingMessage
func NewIncomingMessageFromUint8Content(
	category internalusbcdcenums.IncomingCategory,
	content uint8,
) *IncomingMessage {
	return &IncomingMessage{
		Category: category,
		Content:  fmt.Sprintf("%d", content),
	}
}

// NewIncomingStatusMessage creates a new instance of IncomingMessage with status content
//
// Parameters:
//
// status: The status content of the message
//
// Returns:
//
// An instance of IncomingMessage
func NewIncomingStatusMessage(
	status internalusbcdcenums.IncomingStatus,
) *IncomingMessage {
	return NewIncomingMessageFromUint8Content(
		internalusbcdcenums.IncomingCategoryStatus,
		uint8(status),
	)
}

// String returns a string representation of the IncomingMessage
//
// Returns:
//
// A string that represents the IncomingMessage
func (msg *IncomingMessage) String() string {
	var sb strings.Builder
	sb.WriteByte(msg.Category.Uint8())
	sb.WriteString(msg.Content)
	sb.WriteByte(EndChar)
	return sb.String()
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
func (msg *IncomingMessage) IsEqual(other *IncomingMessage) bool {
	// Check if the instance to be compared is nil
	if other == nil {
		return false
	}
	return msg.Category == other.Category && msg.Content == other.Content
}

// NewIncomingMessageFromString creates an instance of IncomingMessage from a given string
//
// Parameters:
//
// message: The string representation of the message
//
// Returns:
//
// An instance of IncomingMessage, or an error if the string is invalid
func NewIncomingMessageFromString(message string) (*IncomingMessage, error) {
	// Remove the end character if present
	if len(message) > 0 && message[len(message)-1] == EndChar {
		message = message[:len(message)-1]
	}

	// Convert the category string to a Category enum value
	category, err := internalusbcdcenums.IncomingCategoryFromUint8(message[0])
	if err != nil {
		return nil, err
	}

	// Check if based on the incoming category the message content can be empty or not
	if category == internalusbcdcenums.IncomingCategoryMotorSpeedStop ||
		category == internalusbcdcenums.IncomingCategoryServoDirectionCenter ||
		category == internalusbcdcenums.IncomingCategoryGetMaxMotorSpeedValue ||
		category == internalusbcdcenums.IncomingCategoryGetMaxServoDirectionValue {
		return NewIncomingMessage(category, ""), nil
	}

	// Check if the message has content
	if len(message) < 2 {
		return nil, fmt.Errorf(
			"message content cannot be empty for category %s",
			category.Name(),
		)
	}

	// Create and return the IncomingMessage object
	return NewIncomingMessage(category, message[1:]), nil
}

// IsAServoMessage checks if the IncomingMessage is a servo-related message
//
// Returns:
//
// True if the message is related to servo operations, otherwise False
func (msg *IncomingMessage) IsAServoMessage() bool {
	return msg.Category.IsAServoCategory()
}

// IsAMotorMessage checks if the IncomingMessage is a motor-related message
//
// Returns:
//
// True if the message is related to motor operations, otherwise False
func (msg *IncomingMessage) IsAMotorMessage() bool {
	return msg.Category.IsAMotorCategory()
}

// FormatToSendAsAnErrorMessage formats the message to send as an error message.
//
// Returns:
//
// The formatted error message string.
func (msg *IncomingMessage) FormatToSendAsAnErrorMessage() string {
	// Format the message as an error message
	return fmt.Sprintf(
		"%d%s",
		msg.Category,
		msg.Content,
	)
}

// GetContentAsUint16 converts the Content of the IncomingMessage to a uint16 value
//
// Returns:
//
// The uint16 representation of the Content, or an error if the conversion fails
func (msg *IncomingMessage) GetContentAsUint16() (uint16, error) {
	// Convert the content to uint16
	u, err := strconv.ParseUint(msg.Content, 10, 16)
	if err != nil {
		return 0, fmt.Errorf("invalid uint16 value %q: %w", msg.Content, err)
	}
	return uint16(u), nil
}
