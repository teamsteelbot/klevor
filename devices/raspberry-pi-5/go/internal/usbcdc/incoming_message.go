package usbcdc

import (
	"bytes"
	"encoding/binary"
	"fmt"
	"math"

	goconcurrentlogger "github.com/ralvarezdev/go-concurrent-logger"
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

// NewIncomingMessagesFromBuffer creates multiple instances of IncomingMessage from a given bytes buffer
//
// Parameters:
//
// buffer: The buffer to parse for incoming messages
// logger: The logger to use for logging
//
// Returns:
//
// A slice of IncomingMessage instances, or an error if the buffer is invalid
func NewIncomingMessagesFromBuffer(
	buffer *[]byte,
	logger goconcurrentlogger.LoggerProducer,
) ([]*IncomingMessage, error) {
	// Check if the buffer is nil
	if buffer == nil {
		return nil, ErrNilBuffer
	}

	// Parse the buffer to extract messages
	var messages []*IncomingMessage
	for len(*buffer) > 0 {
		// If no start byte is found, return an empty slice
		nextStart := bytes.IndexByte(*buffer, StartAndEndByte)

		// If no start byte is found, exit the loop
		if nextStart == -1 {
			break
		}

		// Remove any bytes before the start byte
		*buffer = (*buffer)[nextStart:]

		// If the buffer length is less than the minimum message length, wait for more data
		if len(*buffer) < 4 {
			break
		}

		// Check if the next bytes are start and bytes, if so omit them
		for len(*buffer) > 1 && (*buffer)[1] == StartAndEndByte {
			// Remove the start byte
			*buffer = (*buffer)[1:]
		}

		// Get the category of the message
		categoryUint8 := (*buffer)[1]
		category, err := IncomingCategoryFromUint8(categoryUint8)
		if err != nil {
			// Log the error and continue to the next potential message
			if logger != nil {
				logger.Warning(
					fmt.Sprintf(
						"An error occurred while parsing incoming messages: %v",
						err,
					),
				)
			}

			// Skip to next start byte
			*buffer = (*buffer)[1:]
			continue
		}

		// Get the data length of the message
		dataLength := uint8((*buffer)[2])

		// Get the expected length of the data for the category
		expectedDataLength, err := category.DataLength()
		if err != nil {
			// Log the error and continue to the next potential message
			if logger != nil {
				logger.Warning(
					fmt.Sprintf(
						"An error occurred while parsing incoming messages: %v",
						err,
					),
				)
			}

			// Skip to next start byte
			*buffer = (*buffer)[2:]
			continue
		}

		// Get the data length of the message
		if dataLength != uint8(expectedDataLength) {
			// Log the error and continue to the next potential message
			if logger != nil {
				logger.Warning(
					fmt.Sprintf(
						"Data length byte mismatch for incoming message of category 0x%02X: expected %d, got %d",
						categoryUint8,
						expectedDataLength,
						dataLength,
					),
				)
			}

			// Skip to next start byte
			*buffer = (*buffer)[2:]
			continue
		}

		// Find the end byte
		data := make([]byte, 0, dataLength)
		maxIndex := int(dataLength) + 3
		for i := 3; i < maxIndex; i++ {
			// Check if we've reached the end of the buffer
			if i >= len(*buffer) {
				break
			}

			// Get the current byte
			b := (*buffer)[i]

			// Check if it's control byte
			if b == ControlByte {
				// Check if there's a next byte
				if i+1 >= len(*buffer) {
					break
				}

				// XOR the next byte with the XOR byte
				data = append(data, (*buffer)[i+1]^XORByte)

				// Skip the next byte
				i++
				maxIndex++
				continue
			}

			// Append the byte to the data
			data = append(data, b)
		}

		// Check if the message is complete
		if dataLength != uint8(len(data)) {
			break
		}

		// Check if it contains the checksum byte and the end byte
		if len(*buffer) < maxIndex+1 {
			break
		}

		// Get the checksum byte
		checksum := (*buffer)[maxIndex]
		if checksum != CalculateChecksum(byte(category), data) {
			// Log the error and continue to the next potential message
			if logger != nil {
				logger.Warning(
					fmt.Sprintf(
						"Checksum byte mismatch for incoming message of category 0x%02X: expected 0x%02X, got 0x%02X",
						categoryUint8,
						CalculateChecksum(byte(category), data),
						checksum,
					),
				)
			}

			// Skip to next start byte
			*buffer = (*buffer)[maxIndex+1:]
			continue
		}

		// Create a new IncomingMessage instance
		messages = append(messages, NewIncomingMessage(category, data))

		// Update the buffer to remove processed messages
		if len(*buffer) == maxIndex+1 {
			*buffer = (*buffer)[:0]
		} else {
			*buffer = (*buffer)[maxIndex+1:]
		}
	}

	return messages, nil
}

// StringToPrint returns a human-readable string representation of the IncomingMessage
//
// Returns:
//
// A human-readable string that represents the IncomingMessage
func (msg *IncomingMessage) StringToPrint() string {
	var dataDetails string

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
			dataDetails = fmt.Sprintf(
				"invalid length: %d, expected: 8",
				len(msg.Data),
			)
			break
		}

		// Extract the float64 value from the message data
		bits := binary.BigEndian.Uint64(msg.Data[:])
		value := math.Float64frombits(bits)
		dataDetails = fmt.Sprintf("%f", value)
	case IncomingCategoryMaxMotorSpeedValue,
		IncomingCategoryMaxServoAngleValue:
		// Check if the data length is valid for an uint16 value
		if len(msg.Data) != 2 {
			dataDetails = fmt.Sprintf(
				"invalid length: %d, expected: 2",
				len(msg.Data),
			)
			break
		}

		// Extract the uint16 value from the message data
		value := binary.BigEndian.Uint16(msg.Data[:])
		dataDetails = fmt.Sprintf("%d", value)
	case IncomingCategoryError:
		// Check if the data length is valid for an uint16 value
		if len(msg.Data) != 2 {
			dataDetails = fmt.Sprintf(
				"invalid length: %d, expected: 2",
				len(msg.Data),
			)
			break
		}

		// Extract the uint16 value from the message data
		value := binary.BigEndian.Uint16(msg.Data[:])

		// Get the error message from the common error codes package. If not found, try to get it from the local error codes
		errorCodeMessage, ok := GetErrorCodeMessage(tinygoerrors.ErrorCode(value))
		if !ok {
			errorCodeMessage = "unknown error code"
		}
		dataDetails = errorCodeMessage
	case IncomingCategoryChallenge:
		challenge, err := internal.ChallengeFromBytes(msg.Data)
		if err != nil {
			dataDetails = fmt.Sprintf("invalid challenge: %v", err)
			break
		}
		if challenge != internal.ChallengeNil {
			dataDetails = challenge.String()
			break
		}
		dataDetails = "nil challenge"
	case IncomingCategoryStatus:
		incomingStatus, err := IncomingStatusFromBytes(msg.Data)
		if err != nil {
			dataDetails = fmt.Sprintf("invalid status: %v", err)
			break
		}
		if incomingStatus != IncomingStatusNil {
			dataDetails = incomingStatus.String()
			break
		}
		dataDetails = "nil status"
	}

	// Check if there are no details for the data
	if dataDetails == "" {
		return fmt.Sprintf(
			"IncomingMessage{Category: [0x%02X] (%s), Data: [%s]}",
			uint8(msg.Category),
			msg.Category.String(),
			ConvertBytesSliceToHexString(msg.Data),
		)
	}

	// Return the formatted string with details
	return fmt.Sprintf(
		"IncomingMessage{Category: [0x%02X] (%s), Data: [%s] (%s)}",
		uint8(msg.Category),
		msg.Category.String(),
		ConvertBytesSliceToHexString(msg.Data),
		dataDetails,
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

// IsStatusStartMessage checks if the IncomingMessage is a status start message
//
// Returns:
//
// True if the message is a status start message, otherwise False
func (msg *IncomingMessage) IsStatusStartMessage() bool {
	return msg.Category == IncomingCategoryStatus && len(msg.Data) == 1 && msg.Data[0] == uint8(IncomingStatusStart)
}