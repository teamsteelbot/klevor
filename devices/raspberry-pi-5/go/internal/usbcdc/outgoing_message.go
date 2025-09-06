package usbcdc

import (
	"fmt"
	"strings"

	internalusbcdcenums "github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal/usbcdc/enums"
)

type (
	// OutgoingMessage is the struct to handle the messages sent to the Raspberry Pi 5
	OutgoingMessage struct {
		Category internalusbcdcenums.OutgoingCategory
		Content  string
	}
)

// NewOutgoingMessage creates a new instance of OutgoingMessage
//
// Parameters:
//
// category: The category of the message
// content: The content of the message
//
// Returns:
//
// An instance of OutgoingMessage
func NewOutgoingMessage(
	category internalusbcdcenums.OutgoingCategory,
	content string,
) *OutgoingMessage {
	return &OutgoingMessage{
		Category: category,
		Content:  strings.TrimSpace(content),
	}
}

// NewOutgoingMessageFromUint8Content creates a new instance of OutgoingMessage with uint8 content
//
// Parameters:
//
// category: The category of the message
// content: The uint8 content of the message
//
// Returns:
//
// An instance of OutgoingMessage
func NewOutgoingMessageFromUint8Content(
	category internalusbcdcenums.OutgoingCategory,
	content uint8,
) *OutgoingMessage {
	return &OutgoingMessage{
		Category: category,
		Content:  fmt.Sprintf("%d", content),
	}
}

// NewOutgoingStatusMessage creates a new instance of OutgoingMessage with status content
//
// Parameters:
//
// status: The status content of the message
//
// Returns:
//
// An instance of OutgoingMessage
func NewOutgoingStatusMessage(
	status internalusbcdcenums.OutgoingStatus,
) *OutgoingMessage {
	return NewOutgoingMessageFromUint8Content(
		internalusbcdcenums.OutgoingCategoryStatus,
		uint8(status),
	)
}

// NewOutgoingMessageFromUint16Content creates a new instance of OutgoingMessage with uint16 content
//
// Parameters:
//
// category: The category of the message
// content: The uint16 content of the message
//
// Returns:
//
// An instance of OutgoingMessage
func NewOutgoingMessageFromUint16Content(
	category internalusbcdcenums.OutgoingCategory,
	content uint16,
) *OutgoingMessage {
	return &OutgoingMessage{
		Category: category,
		Content:  fmt.Sprintf("%d", content),
	}
}

// NewOutgoingMessageFromFloat64Content creates a new instance of OutgoingMessage with float64 content
//
// Parameters:
//
// category: The category of the message
// content: The float64 content of the message
//
// Returns:
//
// An instance of OutgoingMessage
func NewOutgoingMessageFromFloat64Content(
	category internalusbcdcenums.OutgoingCategory,
	content float64,
) *OutgoingMessage {
	return &OutgoingMessage{
		Category: category,
		Content:  fmt.Sprintf("%f", content),
	}
}

// NewOutgoingMessageFromIntContent creates a new instance of OutgoingMessage with int content
//
// Parameters:
//
// category: The category of the message
// content: The int content of the message
//
// Returns:
//
// An instance of OutgoingMessage
func NewOutgoingMessageFromIntContent(
	category internalusbcdcenums.OutgoingCategory,
	content int,
) *OutgoingMessage {
	return &OutgoingMessage{
		Category: category,
		Content:  fmt.Sprintf("%d", content),
	}
}

// String returns a string representation of the OutgoingMessage
//
// Returns:
//
// A string that represents the OutgoingMessage
func (msg *OutgoingMessage) String() string {
	var sb strings.Builder
	sb.WriteByte(byte(msg.Category))
	sb.WriteString(msg.Content)
	sb.WriteByte(EndChar)
	return sb.String()
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
	return msg.Category == other.Category && msg.Content == other.Content
}

// NewOutgoingMessageFromString creates an instance of OutgoingMessage from a given string
//
// Parameters:
//
// message: The string representation of the message
//
// Returns:
//
// An instance of OutgoingMessage, or an error if the string is invalid
func NewOutgoingMessageFromString(message string) (*OutgoingMessage, error) {
	// Remove the end character if present
	if len(message) > 0 && message[len(message)-1] == EndChar {
		message = message[:len(message)-1]
	}

	// Convert the category string to a Category enum value
	category, err := internalusbcdcenums.OutgoingCategoryFromUint8(message[0])
	if err != nil {
		return nil, err
	}

	// Check if based on the incoming category the message content can be empty or not
	if category == internalusbcdcenums.OutgoingCategoryMotorSpeedStop ||
		category == internalusbcdcenums.OutgoingCategoryServoDirectionCenter ||
		category == internalusbcdcenums.OutgoingCategoryGetMaxMotorSpeedValue ||
		category == internalusbcdcenums.OutgoingCategoryGetMaxServoDirectionValue {
		return NewOutgoingMessage(category, ""), nil
	}

	// Check if the message has content
	if len(message) < 2 {
		return nil, fmt.Errorf(
			"message content cannot be empty for category %s",
			category.String(),
		)
	}

	// Create and return the OutgoingMessage object
	return NewOutgoingMessage(category, message[1:]), nil
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

// FormatToSendAsAnErrorMessage formats the message to send as an error message.
//
// Returns:
//
// The formatted error message string.
func (msg *OutgoingMessage) FormatToSendAsAnErrorMessage() string {
	// Format the message as an error message
	return fmt.Sprintf(
		"%d%s",
		msg.Category,
		msg.Content,
	)
}
