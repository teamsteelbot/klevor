package usbcdc

import (
	internalchallenge "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/challenge"
	tinygoerrors "github.com/ralvarezdev/tinygo-errors"
	tinygobuffers "github.com/ralvarezdev/tinygo-buffers"
)

type (
	// OutgoingMessage is the struct to handle the messages sent to the Raspberry Pi 5
	OutgoingMessage struct {
		Category OutgoingCategory
		Data []byte
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
) OutgoingMessage {
	return OutgoingMessage{
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
// buffer: The buffer to use for the message
//
// Returns:
//
// An instance of OutgoingMessage, or an error if the buffer is nil or too small
func NewOutgoingMessageFromUint8Data(
	category OutgoingCategory,
	data uint8,
	buffer []byte,
) (OutgoingMessage, tinygoerrors.ErrorCode) {
	// Check if the buffer is nil or too small
	if buffer == nil || len(buffer) < Uint8BufferSize {
		return OutgoingMessage{}, ErrorCodeUSBCDCBufferTooShortForRawUint8
	}

	// Convert the uint8 to raw bytes
	buffer[0] = data

	return NewOutgoingMessage(
		category,
		buffer[:Uint8BufferSize],
	), tinygoerrors.ErrorCodeNil
}

// NewOutgoingStatusMessage creates a new instance of OutgoingMessage with status content
//
// Parameters:
//
// status: The status content of the message
// buffer: The buffer to use for the message
//
// Returns:
//
// An instance of OutgoingMessage, or an error if the buffer is nil or too small
func NewOutgoingStatusMessage(
	status OutgoingStatus,
	buffer []byte,
) (OutgoingMessage, tinygoerrors.ErrorCode) {
	return NewOutgoingMessageFromUint8Data(
		OutgoingCategoryStatus,
		uint8(status),
		buffer,
	)
}

// NewOutgoingChallengeMessage creates a new instance of OutgoingMessage with challenge content
//
// Parameters:
//
// challenge: The challenge content of the message
// buffer: The buffer to use for the message
//
// Returns:
//
// An instance of OutgoingMessage, or an error if the buffer is nil or too small
func NewOutgoingChallengeMessage(
	challenge internalchallenge.Challenge,
	buffer []byte,
) (OutgoingMessage, tinygoerrors.ErrorCode) {
	return NewOutgoingMessageFromUint8Data(
		OutgoingCategoryChallenge,
		uint8(challenge),
		buffer,
	)
}

// NewOutgoingMessageFromUint16Data creates a new instance of OutgoingMessage with uint16 data
//
// Parameters:
//
// category: The category of the message
// data: The uint16 data of the message
// buffer: The buffer to use for the message
//
// Returns:
//
// An instance of OutgoingMessage, or an error if the buffer is nil or too small
func NewOutgoingMessageFromUint16Data(
	category OutgoingCategory,
	data uint16,
	buffer []byte,
) (OutgoingMessage, tinygoerrors.ErrorCode) {
	// Check if the buffer is nil or too small
	if buffer == nil || len(buffer) < Uint16BufferSize {
		return OutgoingMessage{}, ErrorCodeUSBCDCBufferTooShortForRawUint16
	}

	// Convert the uint16 to raw bytes
	tinygobuffers.Uint16ToBytes(data, buffer)

	return NewOutgoingMessage(
		category,
		buffer[:Uint16BufferSize],
	), tinygoerrors.ErrorCodeNil
}

// NewOutgoingErrorMessage creates a new instance of OutgoingMessage with error content
//
// Parameters:
//
// err: The error content of the message
// buffer: The buffer to use for the message
//
// Returns:
//
// An instance of OutgoingMessage, or an error if the buffer is nil or too small
func NewOutgoingErrorMessage(
	err tinygoerrors.ErrorCode,
	buffer []byte,
) (OutgoingMessage, tinygoerrors.ErrorCode) {
	return NewOutgoingMessageFromUint16Data(
		OutgoingCategoryError,
		uint16(err),
		buffer,
	)
}

// NewOutgoingMessageFromFloat64Data creates a new instance of OutgoingMessage with float64 data
//
// Parameters:
//
// category: The category of the message
// value: The float64 value of the message
// buffer: The buffer to use for the message
//
// Returns:
//
// An instance of OutgoingMessage, or an error if the buffer is nil or too small
func NewOutgoingMessageFromFloat64Data(
	category OutgoingCategory,
	value float64,
	buffer []byte,
) (OutgoingMessage, tinygoerrors.ErrorCode) {
	// Check if the buffer is nil or too small
	if buffer == nil || len(buffer) < Float64BufferSize {
		return OutgoingMessage{}, ErrorCodeUSBCDCBufferTooShortForRawFloat64
	}

	// Convert the float64 to raw bytes
	tinygobuffers.Float64ToBytes(value, buffer)

	return NewOutgoingMessage(
		category,
		buffer[:Float64BufferSize],
	), tinygoerrors.ErrorCodeNil
}