package usbcdc

import (
	"fmt"
	"strings"

	internalusbcdcenums "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/usbcdc/enums"
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

	// Create and return the OutgoingMessage object
	return NewOutgoingMessage(category, message[1:]), nil
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
