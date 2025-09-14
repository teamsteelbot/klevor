package usbcdc

import (
	"math"
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
		messageBuffer []byte
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

	// Check if the MaxIncomingMessageDataSize and MaxOutgoingMessageDataSize are valid
	if MaxIncomingMessageDataSize < 0 || MaxOutgoingMessageDataSize < 0 {
		return nil, ErrorCodeUSBCDCInvalidMaxMessageDataSize
	}

	// Create a buffer big enough to hold the maximum incoming message data size and outgoing message data size
	var messageBuffer []byte
	if MaxIncomingMessageDataSize >= MaxOutgoingMessageDataSize {
		messageBuffer = make([]byte, MaxIncomingMessageDataSize)
	} else {
		messageBuffer = make([]byte, MaxOutgoingMessageDataSize)
	}

	// Return the new DefaultHandler instance
	return &DefaultHandler{
		challengeHandler: challengeHandler,
		ledHandler:       ledHandler,
		serialer:         machine.USBCDC,
		messageBuffer:    messageBuffer,
	}, tinygotypes.ErrorCodeNil
}

// Update receives messages from the USB CDC.
//
// Returns:
//
// An error if it fails to receive messages
func (d *DefaultHandler) Update() tinygotypes.ErrorCode {
	// If no messages are received, turn off the LED
	if d.serialer.Buffered() == 0 {
		if d.ledHandler.IsOn() {
			d.ledHandler.SetOff()
		}
		return tinygotypes.ErrorCodeNil
	}

	// Turn on the LED to indicate a message has been received
	if d.ledHandler.IsOff() {
		d.ledHandler.SetOn()
	}

	// Clear the existing incoming messages
	for i := range d.incomingMessages {
		d.incomingMessages[i] = nil
	}

	// Initialize a slice to hold the messages and a buffer to hold the incoming data
	for idx := 0; idx < IncomingMessagesBufferSize; idx++ {
		for d.serialer.Buffered() > 0 {
			// Read a byte from the serial port
			c, err := d.serialer.ReadByte()
			if err != nil {
				return ErrorCodeUSBCDCFailedReadingFromSerial
			}

			// Add the byte to the buffer
			d.buffer[d.bufferIndex] = c

			// If the byte is not the end character, continue reading
			if c != EndChar {
				d.bufferIndex++
				continue
			}

			// Process the buffer to create an IncomingMessage
			message, errCode := NewIncomingMessage(d.buffer)
			if errCode != tinygotypes.ErrorCodeNil {
				return errCode
			}
			d.incomingMessages[idx] = message

			// Clear the buffer
			d.bufferIndex = 0
			for i := range d.buffer {
				d.buffer[i] = 0
			}
			break
		}
	}
	return tinygotypes.ErrorCodeNil
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
	if err := d.serialer.WriteByte(StartAndEndChar); err != nil {
		return ErrorCodeUSBCDCFailedToSendStartCharacter
	}

	// Send the message category byte
	if err := d.serialer.WriteByte(message.Category); err != nil {
		return ErrorCodeBNO08XFailedToSendOutgoingCategory
	}

	// Send data length byte
	dataLength := len(message.Data)
	if dataLength > math.MaxUint8 {
		return ErrorCodeUSBCDCOutgoingMessageDataTooLarge
	}
	if err := d.serialer.WriteByte(uint8(dataLength)); err != nil {
		return ErrorCodeUSBCDCFailedToSendControlCharacter
	}

	// Send the message data bytes
	for _, b := range message.Data {
		// If the byte is a special character, send the control character first
		if b == StartAndEndChar || b == ControlChar {
			if err := d.serialer.WriteByte(ControlChar); err != nil {
				return ErrorCodeUSBCDCFailedToSendControlCharacter
			}
			b ^= 0x20 // XOR the byte with 0x20
		}
		if err := d.serialer.WriteByte(b); err != nil {
			return ErrorCodeUSBCDCFailedToSendMessageContent
		}
	}

	// Send the end character
	if err := d.serialer.WriteByte(StartAndEndChar); err != nil {
		return ErrorCodeUSBCDCFailedToSendEndCharacter
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
			return ErrorCodeBNO08XUnknownQuaternionIndex
		}

		// Create the message for the current quaternion component
		message, err := NewOutgoingMessageFromFloat64Data(
			category,
			value,
			d.messageBuffer[:Float64BufferSize],
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
			return ErrorCodeBNO08XUnknownEulerDegreesIndex
		}

		// Create the message for the current Euler angle
		message, err := NewOutgoingMessageFromFloat64Data(
			category,
			value,
			d.messageBuffer[:Float64BufferSize],
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
		d.messageBuffer[:Uint8BufferSize],
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
		d.messageBuffer[:Uint16BufferSize],
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
		d.messageBuffer[:Uint8BufferSize],
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
		d.messageBuffer[:Uint8BufferSize],
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
		d.messageBuffer[:Uint16BufferSize],
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
		d.messageBuffer[:Uint16BufferSize],
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
		// Read packet 
		packet, err := d.ReadPacket(timeout - time.Since(startTime))
		if err != tinygotypes.ErrorCodeNil {
			return err
		}

		// Check if any of the received messages is the confirmation message
		if packet.Category == IncomingCategoryStatus && len(packet.Data) == 1 {
			if packet.Data[0] == byte(OutgoingStatusOK) {
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
