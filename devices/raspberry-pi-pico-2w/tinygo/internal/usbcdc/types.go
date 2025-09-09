package usbcdc

import (
	"time"

	"machine"

	internalchallenge "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/challenge"
	internalled "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/led"
	tinygotypes "github.com/ralvarezdev/tinygo-types"
)

type (
	// DefaultHandler is the default implementation of the Handler interface.
	DefaultHandler struct {
		challengeHandler internalchallenge.Handler
		ledHandler       internalled.Handler
		serialer         machine.Serialer
		incomingMessages []*IncomingMessage
		buffer           []byte
		bufferIndex      uint8
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

	return &DefaultHandler{
		challengeHandler: challengeHandler,
		ledHandler:       ledHandler,
		serialer:         machine.USBCDC,
		incomingMessages: make([]*IncomingMessage, IncomingMessagesBufferSize),
		buffer:           make([]byte, 0, BufferSize),
		bufferIndex:      0,
	}, tinygotypes.ErrorCodeNil
}

// GetIncomingMessages returns the incoming messages received from the USB CDC.
//
// Returns:
//
// A slice of pointers to IncomingMessage instances.
func (d *DefaultHandler) GetIncomingMessages() []*IncomingMessage {
	return d.incomingMessages
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
			message, err := NewIncomingMessage(d.buffer)
			if err != tinygotypes.ErrorCodeNil {
				return err
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
func (d *DefaultHandler) SendMessage(message *OutgoingMessage) tinygotypes.ErrorCode {
	// Check if the message is nil
	if message == nil {
		return ErrorCodeUSBCDCNilOutgoingMessage
	}

	// Send the message to the console port
	if _, err := d.serialer.Write(message.Buffer); err != nil {
		return ErrorCodeUSBCDCFailedToSendMessage
	}
	return tinygotypes.ErrorCodeNil
}

// WaitForConfirmationMessage waits for a confirmation message from the USB CDC.
//
// Parameters:
//
// messageToConfirm: The message to confirm
// timeout: The maximum time to wait for the confirmation message
//
// Returns:
//
// An error if it fails to receive the confirmation message within the timeout
func (d *DefaultHandler) WaitForConfirmationMessage(
	messageToConfirm *OutgoingMessage,
	timeout time.Duration,
) tinygotypes.ErrorCode {
	startTime := time.Now()
	for time.Since(startTime) < timeout {
		if err := d.Update(); err != tinygotypes.ErrorCodeNil {
			return err
		}

		// Check if any of the received messages is the confirmation message
		for _, message := range d.incomingMessages {
			if message != nil && message.IsEqual(IncomingOKMessage) {
				return tinygotypes.ErrorCodeNil
			}
		}
	}
	return ErrorCodeUSBCDCConfirmationMessageTimeout
}

// SendConfirmationMessage sends a confirmation message through the USB CDC.
//
// Returns:
//
// An error if it fails to send the confirmation message
func (d *DefaultHandler) SendConfirmationMessage() tinygotypes.ErrorCode {
	return d.SendMessage(OutgoingOKMessage)
}

// SendInitializationMessage sends an initialization message to the USB CDC.
//
// Returns:
//
// An error if it fails to send the initialization message
func (d *DefaultHandler) SendInitializationMessage() tinygotypes.ErrorCode {
	// Send the end character message to indicate initialization
	return d.serialer.WriteByte(EndChar)
}

// SendChallengeMessage sends a challenge message to the USB CDC.
//
// Returns:
//
// An error if it fails to send the challenge message or if confirmation is not received
func (d *DefaultHandler) SendChallengeMessage() tinygotypes.ErrorCode {
	// Get the challenge type from the challenge handler
	challengeType := d.challengeHandler.GetChallenge()

	// Send the challenge message based on the challenge type
	var challengeMessage *OutgoingMessage
	if challengeType == internalchallenge.ChallengeWithObstaclesAndParking {
		challengeMessage = OutgoingChallengeWithObstaclesAndParkingMessage
	} else if challengeType == internalchallenge.ChallengeWithObstacles {
		challengeMessage = OutgoingChallengeWithObstaclesMessage
	} else if challengeType == internalchallenge.ChallengeWithoutObstacles {
		challengeMessage = OutgoingChallengeWithoutObstaclesMessage
	} else {
		return ErrorCodeUSBCDCUnknownChallengeType
	}

	// Send the challenge message
	if err := d.SendMessage(challengeMessage); err != tinygotypes.ErrorCodeNil {
		return err
	}

	// Wait for confirmation of the challenge message
	return d.WaitForConfirmationMessage(
		challengeMessage,
		ConfirmationMessageTimeout,
	)
}

// SendBNO08XQuaternionsMessages sends BNO08X quaternion messages to the USB CDC.
//
// Parameters:
//
// quaternion: A pointer to an array of 4 float64 values representing the quaternion (x, y, z, w).
//
// Returns:
//
// An error if it fails to send any of the quaternion messages.
func (d *DefaultHandler) SendBNO08XQuaternionsMessages(quaternion *[4]float64) tinygotypes.ErrorCode {
	if quaternion == nil {
		return ErrorCodeUSBCDCNilQuaternion
	}

	// Send the quaternion components as separate messages
	if err := d.SendMessage(NewOutgoingMessageFromFloat64Content(
		OutgoingCategoryQuaternionX,
		quaternion[0],
	)); err != tinygotypes.ErrorCodeNil {
		return err
	}

	if err := d.SendMessage(NewOutgoingMessageFromFloat64Content(
		OutgoingCategoryQuaternionY,
		quaternion[1],
	)); err != tinygotypes.ErrorCodeNil {
		return err
	}

	if err := d.SendMessage(NewOutgoingMessageFromFloat64Content(
		OutgoingCategoryQuaternionZ,
		quaternion[2],
	)); err != tinygotypes.ErrorCodeNil {
		return err
	}
	
	if err := d.SendMessage(NewOutgoingMessageFromFloat64Content(
		OutgoingCategoryQuaternionW,
		quaternion[3],
	)); err != tinygotypes.ErrorCodeNil {
		return err
	}
	return tinygotypes.ErrorCodeNil
}

// SendErrorMessage sends an error message to the USB CDC.
//
// Parameters:
//
// error: The error to send
//
// Returns:
//
// An error if it fails to send the error message
func (d *DefaultHandler) SendErrorMessage(err tinygotypes.ErrorCode) tinygotypes.ErrorCode {
	return d.SendMessage(NewOutgoingErrorMessage(
		err,
	))
}

// SendStartMessage sends a start message to the USB CDC and waits for confirmation.
//
// Returns:
//
// An error if it fails to send the start message
func (d *DefaultHandler) SendStartMessage() tinygotypes.ErrorCode {
	// Send the start message
	if err := d.SendMessage(OutgoingStartMessage); err != tinygotypes.ErrorCodeNil {
		return err
	}

	// Wait for confirmation of the start message
	return d.WaitForConfirmationMessage(
		OutgoingStartMessage,
		ConfirmationMessageTimeout,
	)
}

// Stop is called when the USB CDC is stopped.
func (d *DefaultHandler) Stop() {
	d.ledHandler.SetOff()
}
