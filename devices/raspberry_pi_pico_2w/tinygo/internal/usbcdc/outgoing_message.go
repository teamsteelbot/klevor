package usbcdc

import (
	"fmt"
	"strings"

	"github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/usbcdc/enums"
)

type (
	// OutgoingMessage is the struct to handle the messages sent to the Raspberry Pi 5
	OutgoingMessage struct {
		Category enums.OutgoingCategory
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
	category enums.OutgoingCategory,
	content string,
) *OutgoingMessage {
	return &OutgoingMessage{
		Category: category,
		Content:  content,
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
	category enums.OutgoingCategory,
	content uint8,
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
	return fmt.Sprintf(
		"%02d%d%s%d",
		msg.Category,
		HeaderSeparatorChar,
		msg.Content,
		EndChar,
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

	// Split the string into category and content
	parts := strings.SplitN(
		strings.TrimSpace(message),
		HeaderSeparatorString,
		OutgoingMessageExpectedParts,
	)
	if len(parts) != OutgoingMessageExpectedParts {
		return nil, fmt.Errorf(
			ErrOutgoingMessageMissingParts,
			len(parts),
			OutgoingMessageExpectedParts,
		)
	}

	// Convert the category string to a Category enum value
	category, err := enums.OutgoingCategoryFromString(parts[0])
	if err != nil {
		return nil, err
	}

	// Create and return the OutgoingMessage object
	return NewOutgoingMessage(category, parts[1]), nil
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
