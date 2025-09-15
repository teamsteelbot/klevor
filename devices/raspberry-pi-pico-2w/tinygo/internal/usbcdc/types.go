package usbcdc

import (
	"time"

	"machine"

	internalchallenge "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/challenge"
	internalled "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/led"
	tinygotypes "github.com/ralvarezdev/tinygo-types"
	tinygobno08x "github.com/ralvarezdev/tinygo-bno08x"
)

type (
	// DefaultHandler is the default implementation of the Handler interface.
	DefaultHandler struct {
		challengeHandler internalchallenge.Handler
		ledHandler       internalled.Handler
		serialer         machine.Serialer
		incomingMessageBuffer []byte
		outgoingMessageBuffer []byte
	}
)

// NewDefaultHandler creates a new instance of DefaultHandler
//
// Parameters:
//
// challengeHandler: The challenge handler to use to get the challenge mode
// ledHandler: The LED handler to use to toggle the LED when data is received
//
// Returns:
//
// An instance of DefaultHandler, or an error if any of the handlers is nil
func NewDefaultHandler(
	challengeHandler internalchallenge.Handler,
	ledHandler internalled.Handler,
) (*DefaultHandler, tinygotypes.ErrorCode) {
	// Check if the challengeHandler is nil
	if challengeHandler == nil {
		return nil, internalchallenge.ErrorCodeChallengeNilHandler
	}

	// Check if the ledHandler is nil
	if ledHandler == nil {
		return nil, internalled.ErrorCodeLEDNilHandler
	}

	// Configure the USB CDC serial port
	if err := machine.USBCDC.Configure(
		machine.UARTConfig{
			BaudRate: BaudRate,
		},
	); err != nil {
		return nil, ErrorCodeUSBCDCFailedToConfigureUSBCDC
	}

	// Check if the MaxIncomingMessageDataLength and MaxOutgoingMessageDataLength are valid
	if MaxIncomingMessageDataLength < 0 || MaxOutgoingMessageDataLength < 0 {
		return nil, ErrorCodeUSBCDCInvalidMaxMessageDataLength
	}

	// Return the new DefaultHandler instance
	return &DefaultHandler{
		challengeHandler: challengeHandler,
		ledHandler:       ledHandler,
		serialer:         machine.USBCDC,
		incomingMessageBuffer: make([]byte, MaxIncomingMessageDataLength),
		outgoingMessageBuffer: make([]byte, MaxOutgoingMessageDataLength),
	}, tinygotypes.ErrorCodeNil
}

// IsAvailableToRead checks if there are messages available to read from the USB CDC.
//
// Returns:
//
// true if there are messages available to read, false otherwise
func (d *DefaultHandler) IsAvailableToRead() bool {
	return d.serialer.Buffered() > 0
}

// readByte reads a single byte from the USB CDC.
//
// Parameters:
//
// timeout: The maximum time to wait for a byte
//
// Returns:
//
// The byte read and an error if it fails to read the byte
func (d *DefaultHandler) readByte(timeout time.Duration) (byte, tinygotypes.ErrorCode) {
	startTime := time.Now()
	for time.Since(startTime) < timeout {
		if d.serialer.Buffered() > 0 {
			c, err := d.serialer.ReadByte()
			if err != nil {
				return 0, ErrorCodeUSBCDCFailedReadingFromSerial
			}
			return c, tinygotypes.ErrorCodeNil
		}
	}
	return 0, ErrorCodeUSBCDCReadByteTimeout
}

// ReadMessage reads a message from the USB CDC.
//
// Parameters:
//
// timeout: The maximum time to wait for a message
//
// Returns:
//
// The incoming message and an error if it fails to read the message
func (d *DefaultHandler) ReadMessage(timeout time.Duration) (IncomingMessage, tinygotypes.ErrorCode) {
	// If no messages are received, turn off the LED
	if d.serialer.Buffered() == 0 && d.ledHandler.IsOn() {
		d.ledHandler.SetOff()
	}
	
	startTime := time.Now()
	for time.Since(startTime) < timeout {
		// If there are no bytes available, continue waiting
		if d.serialer.Buffered() == 0 {
			continue
		}

		// Read a byte from the serial port until the start character is found
		for {
			c, err := d.readByte(timeout - time.Since(startTime))
			if err != tinygotypes.ErrorCodeNil {
				return IncomingMessage{}, err
			}
			if c == StartAndEndChar {
				break
			}
		}

		// Get the next byte as the category, omit if it's another start character
		c, err := d.readByte(timeout - time.Since(startTime))
		if err != tinygotypes.ErrorCodeNil {
			return IncomingMessage{}, err
		}
		if c == StartAndEndChar {
			// Read the next byte as the category
			c, err = d.readByte(timeout - time.Since(startTime))
			if err != tinygotypes.ErrorCodeNil {
				return IncomingMessage{}, err
			}
		}
		
		// Convert the byte to IncomingCategory
		category, err := IncomingCategoryFromUint8(c)
		if err != tinygotypes.ErrorCodeNil {
			return IncomingMessage{}, err
		}

		// Get the next byte as the data length
		dataLengthByte, err := d.readByte(timeout - time.Since(startTime))
		if err != tinygotypes.ErrorCodeNil {
			return IncomingMessage{}, err
		}
		dataLength := int(dataLengthByte)

		// Check if the data length is valid
		if dataLength < 0 || dataLength > MaxIncomingMessageDataLength {
			return IncomingMessage{}, ErrorCodeUSBCDCInvalidIncomingMessageDataLength
		}

		// Compare the data length with the expected length for the category
		expectedDataLength, err := category.DataLength()
		if err != tinygotypes.ErrorCodeNil {
			return IncomingMessage{}, err
		}
		if dataLength != expectedDataLength {
			return IncomingMessage{}, ErrorCodeUSBCDCInvalidIncomingMessageDataLength
		}

		// Read the data bytes
		data := d.incomingMessageBuffer[:dataLength]
		for i := 0; i < dataLength; i++ {
			c, err := d.readByte(timeout - time.Since(startTime))
			if err != tinygotypes.ErrorCodeNil {
				return IncomingMessage{}, err
			}
			if c == ControlByte {
				// Read the next byte and XOR it with XORByte
				c, err = d.readByte(timeout - time.Since(startTime))
				if err != tinygotypes.ErrorCodeNil {
					return IncomingMessage{}, err
				}
				c ^= XORByte
			}
			data[i] = c
		}

		// Create the IncomingMessage
		message := IncomingMessage{
			Category: category,
			Data:     data,
		}
		return message, tinygotypes.ErrorCodeNil
	}
	return IncomingMessage{}, ErrorCodeUSBCDCReadMessageTimeout
}

// SendMessage sends a message to the USB CDC.
//
// Parameters:
//
// message: The message to send
//
// Returns:
//
// An error if it fails to send the message
func (d *DefaultHandler) SendMessage(message OutgoingMessage) tinygotypes.ErrorCode {
	// Write the start character
	if err := d.serialer.WriteByte(StartAndEndByte); err != nil {
		return ErrorCodeUSBCDCFailedToSendStartByte
	}

	// Send the message category byte
	if err := d.serialer.WriteByte(uint8(message.Category)); err != nil {
		return ErrorCodeUSBCDCFailedToSendOutgoingCategory
	}

	// Send data length byte
	dataLength := len(message.Data)
	if dataLength > MaxOutgoingMessageDataLength {
		return ErrorCodeUSBCDCInvalidOutgoingMessageDataLength
	}

	// Compare the data length with the expected length for the category
	expectedDataLength, err := message.Category.DataLength()
	if err != tinygotypes.ErrorCodeNil {
		return err
	}
	if dataLength != expectedDataLength {
		return ErrorCodeUSBCDCInvalidOutgoingMessageDataLength
	}

	// Write the data length byte
	if err := d.serialer.WriteByte(uint8(dataLength)); err != nil {
		return ErrorCodeUSBCDCFailedToSendControlByte
	}

	// Send the message data bytes
	for _, b := range message.Data {
		// If the byte is a special character, send the control character first
		if b == StartAndEndChar || b == ControlChar {
			if err := d.serialer.WriteByte(ControlChar); err != nil {
				return ErrorCodeUSBCDCFailedToSendControlByte
			}
			b ^= XORChar // XOR the byte with XORChar
		}
		if err := d.serialer.WriteByte(b); err != nil {
			return ErrorCodeUSBCDCFailedToSendMessageContent
		}
	}

	// Send the end character
	if err := d.serialer.WriteByte(StartAndEndChar); err != nil {
		return ErrorCodeUSBCDCFailedToSendEndByte
	}
	return tinygotypes.ErrorCodeNil
}

// SendInitializationMessage sends an initialization message to the USB CDC.
//
// Returns:
//
// An error if it fails to send the initialization message
func (d *DefaultHandler) SendInitializationMessage() tinygotypes.ErrorCode {
	// Send the start character message to indicate initialization
	if err := d.serialer.WriteByte(StartAndEndChar); err != nil {
		return ErrorCodeUSBCDCFailedToSendInitializationMessage
	}
	return tinygotypes.ErrorCodeNil
}

// SendBNO08XQuaternionMessages sends BNO08X quaternion messages to the USB CDC.
//
// Parameters:
//
// quaternion: An array of 4 float64 values representing the quaternion (x, y, z, w).
//
// Returns:
//
// An error if it fails to send any of the quaternion messages.
func (d *DefaultHandler) SendBNO08XQuaternionMessages(quaternion [4]float64) tinygotypes.ErrorCode {
	for i, value := range quaternion {
		var category OutgoingCategory
		switch i {
		case tinygobno08x.QuaternionXIndex:
			category = OutgoingCategoryQuaternionX
		case tinygobno08x.QuaternionYIndex:
			category = OutgoingCategoryQuaternionY
		case tinygobno08x.QuaternionZIndex:
			category = OutgoingCategoryQuaternionZ
		case tinygobno08x.QuaternionWIndex:
			category = OutgoingCategoryQuaternionW
		default:
			return ErrorCodeUSBCDCUnknownQuaternionIndex
		}

		// Create the message for the current quaternion component
		message, err := NewOutgoingMessageFromFloat64Data(
			category,
			value,
			d.outgoingMessageBuffer[:Float64BufferSize],
		)
		if err != tinygotypes.ErrorCodeNil {
			return err
		}

		// Send the quaternion components as separate messages
		if err = d.SendMessage(message); err != tinygotypes.ErrorCodeNil {
			return err
		}
	}
	return tinygotypes.ErrorCodeNil
}

// SendBNO08XEulerDegreesMessages sends BNO08X Euler degrees messages to the USB CDC.
//
// Parameters:
//
// eulerDegrees: An array of 3 float64 values representing the Euler angles (roll, pitch, yaw).
//
// Returns:
//
// An error if it fails to send any of the Euler degrees messages.
func (d *DefaultHandler) SendBNO08XEulerDegreesMessages(eulerDegrees [3]float64) tinygotypes.ErrorCode {
	for i, value := range eulerDegrees {
		var category OutgoingCategory
		switch i {
		case tinygobno08x.EulerDegreesRollIndex:
			category = OutgoingCategoryEulerDegreesRoll
		case tinygobno08x.EulerDegreesPitchIndex:
			category = OutgoingCategoryEulerDegreesPitch
		case tinygobno08x.EulerDegreesYawIndex:
			category = OutgoingCategoryEulerDegreesYaw
		default:
			return ErrorCodeUSBCDCUnknownEulerDegreesIndex
		}

		// Create the message for the current Euler angle
		message, err := NewOutgoingMessageFromFloat64Data(
			category,
			value,
			d.outgoingMessageBuffer[:Float64BufferSize],
		)
		if err != tinygotypes.ErrorCodeNil {
			return err
		}

		// Send the Euler angles as separate messages
		if err = d.SendMessage(message); err != tinygotypes.ErrorCodeNil {
			return err
		}
	}
	return tinygotypes.ErrorCodeNil
}

// SendChallengeMessage sends a challenge message to the USB CDC.
//
// Returns:
//
// An error if it fails to send the challenge message or if confirmation is not received
func (d *DefaultHandler) SendChallengeMessage() tinygotypes.ErrorCode {
	// Get the challenge type from the challenge handler
	challenge := d.challengeHandler.GetChallenge()

	// Create the challenge message
	challengeMessage, err := NewOutgoingChallengeMessage(
		challenge,
		d.outgoingMessageBuffer[:Uint8BufferSize],
	)
	if err != tinygotypes.ErrorCodeNil {
		return err
	}

	// Send the challenge message
	if err := d.SendMessage(challengeMessage); err != tinygotypes.ErrorCodeNil {
		return err
	}

	// Wait for confirmation of the challenge message
	return d.WaitForConfirmationMessage(
		ConfirmationMessageTimeout,
	)
}

// SendErrorMessage sends an error message to the USB CDC.
//
// Parameters:
//
// errorCode: The error to send
//
// Returns:
//
// An error if it fails to send the error message
func (d *DefaultHandler) SendErrorMessage(errorCode tinygotypes.ErrorCode) tinygotypes.ErrorCode {
	// Create the error message
	errorMessage, err := NewOutgoingErrorMessage(
		errorCode,
		d.outgoingMessageBuffer[:Uint16BufferSize],
	)
	if err != tinygotypes.ErrorCodeNil {
		return err
	}
	return d.SendMessage(errorMessage)
}

// SendStartMessage sends a start message to the USB CDC and waits for confirmation.
//
// Returns:
//
// An error if it fails to send the start message
func (d *DefaultHandler) SendStartMessage() tinygotypes.ErrorCode {
	// Create the start message
	startMessage, err := NewOutgoingStatusMessage(
		OutgoingStatusStart,
		d.outgoingMessageBuffer[:Uint8BufferSize],
	)
	if err != tinygotypes.ErrorCodeNil {
		return err
	}

	// Send the start message
	if err := d.SendMessage(startMessage); err != tinygotypes.ErrorCodeNil {
		return err
	}

	// Wait for confirmation of the start message
	return d.WaitForConfirmationMessage(
		ConfirmationMessageTimeout,
	)
}

// SendConfirmationMessage sends a confirmation message through the USB CDC.
//
// Returns:
//
// An error if it fails to send the confirmation message
func (d *DefaultHandler) SendConfirmationMessage() tinygotypes.ErrorCode {
	// Create the confirmation message
	confirmationMessage, err := NewOutgoingStatusMessage(
		OutgoingStatusOK,
		d.outgoingMessageBuffer[:Uint8BufferSize],
	)
	if err != tinygotypes.ErrorCodeNil {
		return err
	}
	return d.SendMessage(confirmationMessage)
}

// SendMaxMotorSpeedValueMessage sends the maximum motor speed value message to the USB CDC.
//
// Parameters:
//
// maxMotorSpeed: The maximum motor speed value to send
//
// Returns:
//
// An error if it fails to send the maximum motor speed value message
func (d *DefaultHandler) SendMaxMotorSpeedValueMessage(maxMotorSpeed uint16) tinygotypes.ErrorCode {
	// Create the max motor speed value message
	maxMotorSpeedMessage, err := NewOutgoingMessageFromUint16Data(
		OutgoingCategoryMaxMotorSpeedValue,
		maxMotorSpeed,
		d.outgoingMessageBuffer[:Uint16BufferSize],
	)
	if err != tinygotypes.ErrorCodeNil {
		return err
	}
	return d.SendMessage(maxMotorSpeedMessage)
}

// SendMaxServoDirectionValueMessage sends the maximum servo direction value message to the USB CDC.
//
// Parameters:
//
// maxServoDirection: The maximum servo direction value to send
//
// Returns:
//
// An error if it fails to send the maximum servo direction value message
func (d *DefaultHandler) SendMaxServoDirectionValueMessage(maxServoDirection uint16) tinygotypes.ErrorCode {
	// Create the max servo direction value message
	maxServoDirectionMessage, err := NewOutgoingMessageFromUint16Data(
		OutgoingCategoryMaxServoDirectionValue,
		maxServoDirection,
		d.outgoingMessageBuffer[:Uint16BufferSize],
	)
	if err != tinygotypes.ErrorCodeNil {
		return err
	}
	return d.SendMessage(maxServoDirectionMessage)
}

// WaitForConfirmationMessage waits for a confirmation message from the USB CDC.
//
// Parameters:
//
// timeout: The maximum time to wait for the confirmation message
//
// Returns:
//
// An error if it fails to receive the confirmation message within the timeout
func (d *DefaultHandler) WaitForConfirmationMessage(
	timeout time.Duration,
) tinygotypes.ErrorCode {
	startTime := time.Now()
	for time.Since(startTime) < timeout {
		// Read message with the remaining timeout duration
		message, err := d.ReadMessage(timeout - time.Since(startTime))
		if err != tinygotypes.ErrorCodeNil {
			return err
		}

		// Check if any of the received messages is the confirmation message
		if message.Category == IncomingCategoryStatus && len(message.Data) == 1 {
			if message.Data[0] == byte(OutgoingStatusOK) {
				return tinygotypes.ErrorCodeNil
			}
		}
	}
	return ErrorCodeUSBCDCConfirmationMessageTimeout
}

// Stop is called when the USB CDC is stopped.
func (d *DefaultHandler) Stop() {
	d.ledHandler.SetOff()
}
