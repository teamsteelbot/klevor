package usbcdc

import (
	"strconv"

	internalchallenge "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/challenge"
	tinygotypes "github.com/ralvarezdev/tinygo-types"
)

type (
	// OutgoingMessage is the struct to handle the messages sent to the Raspberry Pi 5
	OutgoingMessage struct {
		Category OutgoingCategory
		Buffer []byte
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
	category OutgoingCategory,
	content []byte,
) *OutgoingMessage {
	// Create the buffer with the category, content and end character
	buffer := make([]byte, len(content)+2)
	buffer[0] = uint8(category)
	copy(buffer[1:], content)
	buffer[len(buffer)-1] = EndChar

	return &OutgoingMessage{
		Category: category,
		Buffer:   buffer,
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
	category OutgoingCategory,
	content int,
) *OutgoingMessage {
	return NewOutgoingMessage(
		category,
		[]byte(strconv.Itoa(content)),
	)
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
	category OutgoingCategory,
	content uint8,
) *OutgoingMessage {
	return NewOutgoingMessageFromIntContent(
		category,
		int(content),
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
	category OutgoingCategory,
	content uint16,
) *OutgoingMessage {
	return NewOutgoingMessageFromIntContent(
		category,
		int(content),
	)
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
	status OutgoingStatus,
) *OutgoingMessage {
	return NewOutgoingMessageFromUint8Content(
		OutgoingCategoryStatus,
		uint8(status),
	)
}

// NewOutgoingChallengeMessage creates a new instance of OutgoingMessage with challenge content
//
// Parameters:
//
// challenge: The challenge content of the message
//
// Returns:
//
// An instance of OutgoingMessage
func NewOutgoingChallengeMessage(
	challenge internalchallenge.Challenge,
) *OutgoingMessage {
	return NewOutgoingMessageFromUint8Content(
		OutgoingCategoryChallenge,
		uint8(challenge),
	)
}

// NewOutgoingDebugMessage creates a new instance of OutgoingMessage with debug content
//
// Parameters:
//
// debugInfo: The debug information content of the message
//
// Returns:
//
// An instance of OutgoingMessage
func NewOutgoingDebugMessage(
	debugInfo Debug,
) *OutgoingMessage {
	return NewOutgoingMessageFromUint8Content(
		OutgoingCategoryDebug,
		uint8(debugInfo),
	)
}

// NewOutgoingErrorMessage creates a new instance of OutgoingMessage with error content
//
// Parameters:
//
// err: The error content of the message
//
// Returns:
//
// An instance of OutgoingMessage
func NewOutgoingErrorMessage(
	err tinygotypes.ErrorCode,
) *OutgoingMessage {
	return NewOutgoingMessageFromUint16Content(
		OutgoingCategoryError,
		uint16(err),
	)
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
	category OutgoingCategory,
	content float64,
) *OutgoingMessage {
	return NewOutgoingMessage(
		category,
		[]byte(strconv.FormatFloat(content, 'f', -1, 64)),
	)
}