package usbcdc

import (
	"time"

	"github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal"
	internalusbcdcenums "github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal/usbcdc/enums"
)

const (
	// EndChar is the message end character
	EndChar byte = 0x04

	// BufferSize is the size of the buffer for USB-CDC communication
	BufferSize uint8 = 16

	// ChunkSize is the default size of data chunks
	ChunkSize = 64

	// ConfirmationMessageTimeout is the timeout duration for confirmation messages
	ConfirmationMessageTimeout = time.Second * 5

	// BaudRate is the baud rate for USB-CDC communication
	BaudRate = 921600

	// ConnectionAttempts is the amount of attempts to connect to the serial port
	ConnectionAttempts = 10

	// AttemptsDelay is the delay between connection attempts
	AttemptsDelay = 1 * time.Second

	// StopTimeout is the timeout duration for stopping the USB-CDC communication
	StopTimeout = 5 * time.Second

	// LoggerTag is the logger tag for USB-CDC
	LoggerTag = "USB-CDC"
)

var (
	// OutgoingStopMessage is the outgoing stop message for USB-CDC communication
	OutgoingStopMessage = NewOutgoingMessageFromUint8Content(
		internalusbcdcenums.OutgoingCategoryStatus,
		uint8(internalusbcdcenums.StatusStop),
	)

	// OutgoingOKMessage is the outgoing OK message for USB-CDC communication
	OutgoingOKMessage = NewOutgoingMessageFromUint8Content(
		internalusbcdcenums.OutgoingCategoryStatus,
		uint8(internalusbcdcenums.StatusOK),
	)

	// OutgoingHeartbeatMessage is the outgoing heartbeat message for USB-CDC communication
	OutgoingHeartbeatMessage = NewOutgoingMessageFromUint8Content(
		internalusbcdcenums.OutgoingCategoryStatus,
		uint8(internalusbcdcenums.StatusHeartbeat),
	)

	// IncomingStartMessage is the incoming start message for USB-CDC communication
	IncomingStartMessage = NewIncomingMessageFromUint8Content(
		internalusbcdcenums.IncomingCategoryStatus,
		uint8(internalusbcdcenums.StatusStart),
	)

	// IncomingOKMessage is the incoming OK message for USB-CDC communication
	IncomingOKMessage = NewIncomingMessageFromUint8Content(
		internalusbcdcenums.IncomingCategoryStatus,
		uint8(internalusbcdcenums.StatusOK),
	)

	// IncomingChallengeWithObstaclesMessage is the incoming challenge message with obstacles
	IncomingChallengeWithObstaclesMessage = NewIncomingMessageFromUint8Content(
		internalusbcdcenums.IncomingCategoryChallenge,
		uint8(internal.ChallengeWithObstacles),
	)

	// IncomingChallengeWithObstaclesAndParkingMessage is the incoming challenge message with obstacles and parking
	IncomingChallengeWithObstaclesAndParkingMessage = NewIncomingMessageFromUint8Content(
		internalusbcdcenums.IncomingCategoryChallenge,
		uint8(internal.ChallengeWithObstaclesAndParking),
	)

	// IncomingChallengeWithoutObstaclesMessage is the incoming challenge message without obstacles
	IncomingChallengeWithoutObstaclesMessage = NewIncomingMessageFromUint8Content(
		internalusbcdcenums.IncomingCategoryChallenge,
		uint8(internal.ChallengeWithoutObstacles),
	)
)
