package usbcdc

import (
	"fmt"
	"strings"

	"github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/usbcdc/enums"
)

type (
	// IncomingMessage is the struct to handle the messages received to the Raspberry Pi 5
	IncomingMessage struct {
		Category enums.IncomingCategory
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
	category enums.IncomingCategory,
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
	category enums.IncomingCategory,
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
	return fmt.Sprintf(
		"%02d%d%s%d",
		msg.Category,
		HeaderSeparatorChar,
		msg.Content,
		EndChar,
	)
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
// msgStr: The string representation of the message
//
// Returns:
//
// An instance of IncomingMessage, or an error if the string is invalid
func NewIncomingMessageFromString(msgStr string) (*IncomingMessage, error) {
	// Remove the end character if present
	if len(msgStr) > 0 && msgStr[len(msgStr)-1] == EndChar {
		msgStr = msgStr[:len(msgStr)-1]
	}

	// Split the string into category and content
	parts := strings.SplitN(
		strings.TrimSpace(msgStr),
		HeaderSeparatorString,
		IncomingMessageExpectedParts,
	)
	if len(parts) != IncomingMessageExpectedParts {
		return nil, fmt.Errorf(
			ErrIncomingMessageMissingParts,
			len(parts),
			IncomingMessageExpectedParts,
		)
	}

	// Convert the category string to a Category enum value
	category, err := enums.IncomingCategoryFromString(parts[0])
	if err != nil {
		return nil, err
	}

	// Create and return the IncomingMessage object
	return NewIncomingMessage(category, parts[1]), nil
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
