package usbcdc

import (
	"fmt"
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
		Content:  content,
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

// String returns a string representation of the IncomingMessage
//
// Returns:
//
// A string that represents the IncomingMessage
func (msg *IncomingMessage) String() string {
	var sb strings.Builder
	sb.WriteByte(byte(msg.Category))
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

	// Create and return the IncomingMessage object
	return NewIncomingMessage(category, message[1:]), nil
}

/*
def format_to_send_with_error_message(self) -> str:
"""
Format the message to send with an error message.

Returns:
str: The formatted message string.
"""
return f"{self.__category}{HEADER_SEPARATOR_CHAR}{self.__content}"
*/
