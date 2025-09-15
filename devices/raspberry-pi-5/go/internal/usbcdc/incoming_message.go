package usbcdc

import (
	"bytes"
	"encoding/binary"
	"fmt"
	"math"

	gotinygoerrors "github.com/ralvarezdev/go-tinygo-errors"
	"github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal"
	tinygoerrors "github.com/ralvarezdev/tinygo-errors"
)

type (
	// IncomingMessage is the struct to handle the messages received to the Raspberry Pi 5
	IncomingMessage struct {
		Category IncomingCategory
		Data     []byte
	}
)

// NewIncomingMessage creates a new instance of IncomingMessage
//
// Parameters:
//
// category: The category of the message
// data: The data of the message
//
// Returns:
//
// An instance of IncomingMessage
func NewIncomingMessage(
	category IncomingCategory,
	data []byte,
) *IncomingMessage {
	return &IncomingMessage{
		Category: category,
		Data:     data,
	}
}

// NewIncomingMessageFromUint8Data creates a new instance of IncomingMessage with uint8 data
//
// Parameters:
//
// category: The category of the message
// data: The uint8 data of the message
//
// Returns:
//
// An instance of IncomingMessage
func NewIncomingMessageFromUint8Data(
	category IncomingCategory,
	data uint8,
) *IncomingMessage {
	return NewIncomingMessage(
		category,
		[]byte{data},
	)
}

// NewIncomingStatusMessage creates a new instance of IncomingMessage with status data
//
// Parameters:
//
// status: The status data of the message
//
// Returns:
//
// An instance of IncomingMessage
func NewIncomingStatusMessage(
	status IncomingStatus,
) *IncomingMessage {
	return NewIncomingMessageFromUint8Data(
		IncomingCategoryStatus,
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
	return NewIncomingMessageFromUint8Data(
		IncomingCategoryChallenge,
		uint8(challenge),
	)
}

// StringToPrint returns a human-readable string representation of the IncomingMessage
//
// Returns:
//
// A human-readable string that represents the IncomingMessage
func (msg *IncomingMessage) StringToPrint() string {
	switch msg.Category {
	case IncomingCategoryEulerDegreesPitch,
		IncomingCategoryEulerDegreesRoll,
		IncomingCategoryEulerDegreesYaw,
		IncomingCategoryQuaternionW,
		IncomingCategoryQuaternionX,
		IncomingCategoryQuaternionY,
		IncomingCategoryQuaternionZ:
		// Check if the data length is valid for a float64 value
		if len(msg.Data) != 8 {
			return fmt.Sprintf(
				"IncomingMessage{Category: %s, Data: %q (invalid length: %d, expected: 8)}",
				msg.Category.String(),
				msg.Data,
				len(msg.Data),
			)
		}

		// Extract the float64 value from the message data
		bits := binary.BigEndian.Uint64(msg.Data[:])
		value := math.Float64frombits(bits)
		return fmt.Sprintf(
			"IncomingMessage{Category: %s, Data: %q (%f)}",
			msg.Category.String(),
			msg.Data,
			value,
		)
	case IncomingCategoryMaxMotorSpeedValue,
		IncomingCategoryMaxServoDirectionValue:
		// Check if the data length is valid for an uint16 value
		if len(msg.Data) != 2 {
			return fmt.Sprintf(
				"IncomingMessage{Category: %s, Data: %q (invalid length: %d, expected: 2)}",
				msg.Category.String(),
				msg.Data,
				len(msg.Data),
			)
		}

		// Extract the uint16 value from the message data
		value := binary.BigEndian.Uint16(msg.Data[:])
		return fmt.Sprintf(
			"IncomingMessage{Category: %s, Data: %q (%d)}",
			msg.Category.String(),
			msg.Data,
			value,
		)
	case IncomingCategoryError:
		// Check if the data length is valid for an uint16 value
		if len(msg.Data) != 2 {
			return fmt.Sprintf(
				"IncomingMessage{Category: %s, Data: %q (invalid length: %d, expected: 2)}",
				msg.Category.String(),
				msg.Data,
				len(msg.Data),
			)
		}

		// Extract the uint16 value from the message data
		value := binary.BigEndian.Uint16(msg.Data[:])

		// Get the error message from the common error codes package. If not found, try to get it from the local error codes
		var errorCodeMessage string
		if errorMessage, ok := gotinygoerrors.ErrorCodeMessages[tinygoerrors.ErrorCode(value)]; ok {
			errorCodeMessage = errorMessage
		} else if internalErrorMessage, ok := ErrorCodeMessages[tinygoerrors.ErrorCode(value)]; ok {
			errorCodeMessage = internalErrorMessage
		}

		// If no error message was found, set a default message
		if errorCodeMessage == "" {
			errorCodeMessage = "unknown error code"
		}	

		return fmt.Sprintf(
			"IncomingMessage{Category: %s, Data: %q (%s)}",
			msg.Category.String(),
			msg.Data,
			errorCodeMessage,
		)
	case IncomingCategoryChallenge:
		challenge, err := internal.ChallengeFromBytes(msg.Data)
		if err != nil {
			return fmt.Sprintf(
				"IncomingMessage{Category: %s, Data: %q (invalid challenge: %v)}",
				msg.Category.String(),
				msg.Data,
				err,
			)
		}
		if challenge != internal.ChallengeNil {
			return fmt.Sprintf(
				"IncomingMessage{Category: %s, Data: %q (%s)}",
				msg.Category.String(),
				msg.Data,
				challenge.String(),
			)
		}
		fallthrough
	case IncomingCategoryStatus:
		incomingStatus, err := IncomingStatusFromBytes(msg.Data)
		if err != nil {
			return fmt.Sprintf(
				"IncomingMessage{Category: %s, Data: %q (invalid status: %v)}",
				msg.Category.String(),
				msg.Data,
				err,
			)
		}
		if incomingStatus != IncomingStatusNil {
			return fmt.Sprintf(
				"IncomingMessage{Category: %s, Data: %q (%s)}",
				msg.Category.String(),
				msg.Data,
				incomingStatus.String(),
			)
		}
		fallthrough
	default:
		return fmt.Sprintf(
			"IncomingMessage{Category: %s, Data: %q}",
			msg.Category.String(),
			msg.Data,
		)
	}
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

	// Compare the categories fields
	return msg.Category == other.Category && bytes.Equal(msg.Data, other.Data)
}

// IsAChallengeMessage checks if the IncomingMessage is a challenge message
//
// Returns:
//
// True if the message is a challenge message, otherwise False
func (msg *IncomingMessage) IsAChallengeMessage() bool {
	return msg.Category == IncomingCategoryChallenge
}

// IsAnErrorMessage checks if the IncomingMessage is an error message
//
// Returns:
//
// True if the message is an error message, otherwise False
func (msg *IncomingMessage) IsAnErrorMessage() bool {
	return msg.Category == IncomingCategoryError
}

// IsAQuaternionMessage checks if the IncomingMessage is a quaternion-related message
//
// Returns:
//
// True if the message is related to quaternion operations, otherwise False
func (msg *IncomingMessage) IsAQuaternionMessage() bool {
	return msg.Category == IncomingCategoryQuaternionW ||
		msg.Category == IncomingCategoryQuaternionX ||
		msg.Category == IncomingCategoryQuaternionY ||
		msg.Category == IncomingCategoryQuaternionZ
}

// IsAEulerDegreesMessage checks if the IncomingMessage is an euler-degrees-related message
//
// Returns:
//
// True if the message is related to euler degrees operations, otherwise False
func (msg *IncomingMessage) IsAEulerDegreesMessage() bool {
	return msg.Category == IncomingCategoryEulerDegreesPitch ||
		msg.Category == IncomingCategoryEulerDegreesRoll ||
		msg.Category == IncomingCategoryEulerDegreesYaw
}