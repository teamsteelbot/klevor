package usbcdc

import (
	"time"

	"github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal"
	internalusbcdcenums "github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal/usbcdc/enums"
)

const (
	// EndChar is the message end character
	EndChar byte = 0x04

	// ConfirmationMessageTimeout is the timeout duration for confirmation messages
	ConfirmationMessageTimeout = time.Second * 5

	// StopTimeout is the timeout duration for stopping the USB-CDC communication
	StopTimeout = 5 * time.Second

	// OutgoingWaitTimeout is the timeout duration for waiting for outgoing messages to be sent
	OutgoingWaitTimeout = 5 * time.Second

	// WriteTimeout is the timeout duration for writing to the USB-CDC port
	WriteTimeout = time.Second * 2

	// IncomingDelay is the delay between incoming message checks
	IncomingDelay = 10 * time.Millisecond

	// ConfirmationTimeout is the timeout duration for confirmation messages
	ConfirmationTimeout = 5 * time.Second

	// ReadTimeout is the timeout duration for reading from the USB-CDC port
	ReadTimeout = time.Second * 2

	// ConfirmationAttempts is the number of attempts to confirm a message
	ConfirmationAttempts = ConfirmationTimeout / IncomingDelay
)

var (
	// BufferSize is the size of the buffer for USB-CDC communication
	BufferSize uint8 = 64

	// AccumulatedBufferSize is the size of the accumulated buffer for USB-CDC communication
	AccumulatedBufferSize uint16 = 256

	// ChunkSize is the default size of data chunks
	ChunkSize = 64

	// BaudRate is the baud rate for USB-CDC communication
	BaudRate = 921600

	// ConnectionAttempts is the amount of attempts to connect to the serial port
	ConnectionAttempts = 10

	// AttemptsDelay is the delay between connection attempts
	AttemptsDelay = 1 * time.Second

	// HandlerLoggerProducerTag is the logger producer tag for USB-CDC handler
	HandlerLoggerProducerTag = "USB_CDC_HANDLER"

	// SenderLoggerProducerTag is the logger producer tag for USB-CDC sender
	SenderLoggerProducerTag = "USB_CDC_SENDER"

	// IncomingMessagesChannelBufferSize is the size of the incoming messages channel buffer
	IncomingMessagesChannelBufferSize = 100

	// OutgoingMessagesChannelBufferSize is the size of the outgoing messages channel buffer
	OutgoingMessagesChannelBufferSize = 100

	// OutgoingStopMessage is the outgoing stop message for USB-CDC communication
	OutgoingStopMessage = NewOutgoingStatusMessage(internalusbcdcenums.OutgoingStatusStop)

	// OutgoingOKMessage is the outgoing OK message for USB-CDC communication
	OutgoingOKMessage = NewOutgoingStatusMessage(internalusbcdcenums.OutgoingStatusOK)

	// OutgoingHeartbeatMessage is the outgoing heartbeat message for USB-CDC communication
	OutgoingHeartbeatMessage = NewOutgoingStatusMessage(internalusbcdcenums.OutgoingStatusHeartbeat)

	// IncomingStartMessage is the incoming start message for USB-CDC communication
	IncomingStartMessage = NewIncomingStatusMessage(internalusbcdcenums.IncomingStatusStart)

	// IncomingOKMessage is the incoming OK message for USB-CDC communication
	IncomingOKMessage = NewIncomingStatusMessage(internalusbcdcenums.IncomingStatusOK)

	// IncomingChallengeWithObstaclesMessage is the incoming challenge message with obstacles
	IncomingChallengeWithObstaclesMessage = NewIncomingChallengeMessage(internal.ChallengeWithObstacles)

	// IncomingChallengeWithObstaclesAndParkingMessage is the incoming challenge message with obstacles and parking
	IncomingChallengeWithObstaclesAndParkingMessage = NewIncomingChallengeMessage(internal.ChallengeWithObstaclesAndParking)

	// IncomingChallengeWithoutObstaclesMessage is the incoming challenge message without obstacles
	IncomingChallengeWithoutObstaclesMessage = NewIncomingChallengeMessage(internal.ChallengeWithoutObstacles)
)
