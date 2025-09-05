package usbcdc

import (
	"fmt"
	"strings"
	"time"

	"machine"

	internalchallenge "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/challenge"
	internalchallengeenums "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/challenge/enums"
	internalled "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/led"
	internalusbcdcenums "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/usbcdc/enums"
)

type (
	// DefaultHandler is the default implementation of the Handler interface.
	DefaultHandler struct {
		challengeHandler internalchallenge.Handler
		ledHandler       internalled.Handler
		serialer         machine.Serialer
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
) (*DefaultHandler, error) {
	// Check if the challengeHandler is nil
	if challengeHandler == nil {
		return nil, internalchallenge.ErrNilHandler
	}

	// Check if the ledHandler is nil
	if ledHandler == nil {
		return nil, internalled.ErrNilHandler
	}

	// Configure the USB CDC serial port
	if err := machine.USBCDC.Configure(
		machine.UARTConfig{
			BaudRate: BaudRate,
		},
	); err != nil {
		return nil, fmt.Errorf(ErrFailedToConfigureUSBCDC, err)
	}

	return &DefaultHandler{
		challengeHandler,
		ledHandler,
		machine.USBCDC,
	}, nil
}

// ReceiveMessages receives messages from the USB CDC.
//
// Returns:
//
// A pointer to a list of received messages or an error if it fails to receive messages
func (d *DefaultHandler) ReceiveMessages() (*[]IncomingMessage, error) {
	// If no messages are received, turn off the LED
	if d.serialer.Buffered() == 0 {
		if d.ledHandler.IsOn() {
			d.ledHandler.SetOff()
		}
		return nil, nil
	}

	// Turn on the LED to indicate a message has been received
	if d.ledHandler.IsOff() {
		d.ledHandler.SetOn()
	}

	// Initialize a slice to hold the messages and a buffer to hold the incoming data
	messages := &[]IncomingMessage{}
	buffer := make([]byte, 0, BufferSize)
	for d.serialer.Buffered() > 0 {
		// Read a byte from the serial port
		c, err := d.serialer.ReadByte()
		if err != nil {
			return nil, fmt.Errorf(ErrFailedReadingFromSerial, err)
		}

		// If the byte is the end character, process the buffer
		if c == EndChar {
			messageStr := string(buffer)
			message, err := NewIncomingMessageFromString(messageStr)
			if err != nil {
				return nil, err
			}
			*messages = append(*messages, *message)

			// Clear the buffer
			buffer = make([]byte, 0, BufferSize)
		} else {
			// Otherwise, add the byte to the buffer
			buffer = append(buffer, c)
		}
	}
	return messages, nil
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
func (d *DefaultHandler) SendMessage(message *OutgoingMessage) error {
	// Check if the message is nil
	if message == nil {
		return ErrNilOutgoingMessage
	}

	// Send the message to the console port
	if _, err := d.serialer.Write([]byte(message.String())); err != nil {
		return fmt.Errorf(ErrFailedToSendMessage, err)
	}
	return nil
}

// SendBufferMessage sends a message in chunks to the USB CDC console stream.
//
// Parameters:
//
// category: The category of the message
// message: The message to send as a Strings.Builder object
//
// Returns:
//
// An error if there is an error in sending the message
func (d *DefaultHandler) SendBufferMessage(
	category internalusbcdcenums.OutgoingCategory,
	message *strings.Builder,
) error {
	// Send the category header
	if category == internalusbcdcenums.OutgoingCategoryNil {
		return fmt.Errorf(ErrNilOutgoingCategory, category)
	}
	d.serialer.WriteByte(
		byte(category),
	)

	// Send the message in chunks
	messageStr := message.String()
	for i := 0; i < len(messageStr); i += ChunkSize {
		// Get the chunk of the message to send
		end := i + ChunkSize
		if end > len(messageStr) {
			end = len(messageStr)
		}
		chunk := messageStr[i:end]

		// Send the chunk to the console port
		if _, err := d.serialer.Write([]byte(chunk)); err != nil {
			return fmt.Errorf(ErrFailedToSendChunkMessage, err)
		}
	}

	// Send the end character to indicate the end of the message
	if err := d.serialer.WriteByte(EndChar); err != nil {
		return fmt.Errorf(ErrFailedToSendEndCharacter, err)
	}
	return nil
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
) error {
	startTime := time.Now()
	for time.Since(startTime) < timeout {
		messages, err := d.ReceiveMessages()
		if err != nil {
			return err
		}
		if messages == nil || len(*messages) == 0 {
			continue
		}

		// Check if any of the received messages is the confirmation message
		for _, message := range *messages {
			if message.IsEqual(IncomingOKMessage) {
				return nil
			}
		}
	}
	return fmt.Errorf(
		ErrConfirmationMessageTimeout,
		messageToConfirm.FormatToSendAsAnErrorMessage(),
		timeout.Seconds(),
	)
}

// SendConfirmationMessage sends a confirmation message through the USB CDC.
//
// Returns:
//
// An error if it fails to send the confirmation message
func (d *DefaultHandler) SendConfirmationMessage() error {
	return d.SendMessage(OutgoingOKMessage)
}

// SendInitializationMessage sends an initialization message to the USB CDC.
//
// Returns:
//
// An error if it fails to send the initialization message
func (d *DefaultHandler) SendInitializationMessage() error {
	// Send the end character message to indicate initialization
	return d.serialer.WriteByte(EndChar)
}

// SendChallengeMessage sends a challenge message to the USB CDC.
//
// Returns:
//
// An error if it fails to send the challenge message or if confirmation is not received
func (d *DefaultHandler) SendChallengeMessage() error {
	// Get the challenge type from the challenge handler
	challengeType := d.challengeHandler.GetChallenge()

	// Send the challenge message based on the challenge type
	var challengeMessage *OutgoingMessage
	if challengeType == internalchallengeenums.ChallengeWithObstaclesAndParking {
		challengeMessage = OutgoingChallengeWithObstaclesAndParkingMessage
	} else if challengeType == internalchallengeenums.ChallengeWithObstacles {
		challengeMessage = OutgoingChallengeWithObstaclesMessage
	} else if challengeType == internalchallengeenums.ChallengeWithoutObstacles {
		challengeMessage = OutgoingChallengeWithoutObstaclesMessage
	} else {
		return fmt.Errorf(ErrUnknownChallengeType, challengeType)
	}

	if err := d.SendMessage(challengeMessage); err != nil {
		return err
	}

	// Wait for confirmation of the challenge message
	return d.WaitForConfirmationMessage(
		challengeMessage,
		ConfirmationMessageTimeout,
	)
}

// SendBNO08XYawDegreesMessage sends a BNO08x yaw degrees message to the USB CDC.
//
// Returns:
//
// An error if it fails to send the yaw degrees message
func (d *DefaultHandler) SendBNO08XYawDegreesMessage(yawDegrees float64) error {
	// Create the BNO08x yaw degrees message
	bno08xMessage := NewOutgoingMessage(
		internalusbcdcenums.OutgoingCategoryBNO08XYawDegrees,
		fmt.Sprintf("%.1f", yawDegrees),
	)

	// Send the BNO08x yaw degrees message
	return d.SendMessage(bno08xMessage)
}

// SendBNO08XYawTurnsMessage sends a BNO08x yaw turns message to the USB CDC.
//
// Parameters:
//
// turns: The number of turns to send
//
// Returns:
//
// An error if it fails to send the yaw turns message
func (d *DefaultHandler) SendBNO08XYawTurnsMessage(turns int) error {
	// Create the BNO08x yaw turns message
	bno08xMessage := NewOutgoingMessageFromIntContent(
		internalusbcdcenums.OutgoingCategoryBNO08XYawTurns,
		turns,
	)

	// Send the BNO08x yaw turns message
	return d.SendMessage(bno08xMessage)
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
func (d *DefaultHandler) SendErrorMessage(err error) error {
	// Check if the error is nil
	if err == nil {
		return nil
	}

	// Create the error message
	errorMessage := NewOutgoingMessage(
		internalusbcdcenums.OutgoingCategoryError,
		err.Error(),
	)

	// Send the error message
	return d.SendMessage(errorMessage)
}

// SendStartMessage sends a start message to the USB CDC and waits for confirmation.
//
// Returns:
//
// An error if it fails to send the start message
func (d *DefaultHandler) SendStartMessage() error {
	// Send the start message
	if err := d.SendMessage(OutgoingStartMessage); err != nil {
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
