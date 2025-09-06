package usbcdc

import (
	"fmt"
	"strconv"
	"strings"

	"github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal"
	internalusbcdcenums "github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal/usbcdc/enums"
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

// NewIncomingChallengeMessage creates a new instance of IncomingMessage with challenge content
//
// Parameters:
//
// challenge: The challenge content of the message
//
// Returns:
//
// An instance of IncomingMessage
func NewIncomingChallengeMessage(
	challenge internal.Challenge,
) *IncomingMessage {
	return NewIncomingMessageFromUint8Content(
		internalusbcdcenums.IncomingCategoryChallenge,
		uint8(challenge),
	)
}

// NewIncomingDebugMessage creates a new instance of IncomingMessage with debug content
//
// Parameters:
//
// debugInfo: The debug information content of the message
//
// Returns:
//
// An instance of IncomingMessage
func NewIncomingDebugMessage(
	debugInfo internalusbcdcenums.Debug,
) *IncomingMessage {
	return NewIncomingMessageFromUint8Content(
		internalusbcdcenums.IncomingCategoryDebug,
		uint8(debugInfo),
	)
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

	// Check if the message has content
	if len(message) < 2 {
		return nil, ErrIncomingMessageWithoutContent
	}

	// Create and return the IncomingMessage object
	return NewIncomingMessage(category, message[1:]), nil
}

// NewIncomingMessagesFromBuffer creates multiple instances of IncomingMessage from a given bytes buffer
//
// Parameters:
//
// buffer: The bytes buffer containing multiple messages
//
// Returns:
//
// A slice of IncomingMessage instances, or an error if the buffer is invalid
func NewIncomingMessagesFromBuffer(buffer *[]byte) ([]*IncomingMessage, error) {
	// Check if the buffer is nil
	if buffer == nil {
		return nil, ErrNilBuffer
	}

	// Parse the buffer to extract messages
	var messages []*IncomingMessage
	var currentMessage []byte
	var lastIndex int
	for i, b := range *buffer {
		if b == EndChar {
			if len(currentMessage) > 0 {
				msg, err := NewIncomingMessageFromString(string(currentMessage))
				if err != nil {
					return nil, err
				}
				messages = append(messages, msg)
				currentMessage = nil
				lastIndex = i + 1
			}
		} else {
			currentMessage = append(currentMessage, b)
		}
	}

	// Update the buffer to remove processed messages
	*buffer = (*buffer)[lastIndex:]

	return messages, nil
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

// IsAChallengeMessage checks if the IncomingMessage is a challenge message
//
// Returns:
//
// True if the message is a challenge message, otherwise False
func (msg *IncomingMessage) IsAChallengeMessage() bool {
	return msg.Category == internalusbcdcenums.IncomingCategoryChallenge
}

// IsAnErrorMessage checks if the IncomingMessage is an error message
//
// Returns:
//
// True if the message is an error message, otherwise False
func (msg *IncomingMessage) IsAnErrorMessage() bool {
	return msg.Category == internalusbcdcenums.IncomingCategoryError
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
