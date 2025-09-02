package usbcdc

import (
	"fmt"
	"time"

	internalchallenge "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/challenge"
	internalchallengeenums "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/challenge/enums"
	internalledonboard "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/led/onboard"
	internalusbcdcenums "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/usbcdc/enums"
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
)

var (
	// IncomingStopMessage is the incoming stop message for USB-CDC communication
	IncomingStopMessage = NewIncomingMessageFromUint8Content(
		internalusbcdcenums.IncomingCategoryStatus,
		uint8(internalusbcdcenums.StatusStop),
	)

	// IncomingOKMessage is the incoming OK message for USB-CDC communication
	IncomingOKMessage = NewIncomingMessageFromUint8Content(
		internalusbcdcenums.IncomingCategoryStatus,
		uint8(internalusbcdcenums.StatusOK),
	)

	// IncomingHeartbeatMessage is the incoming heartbeat message for USB-CDC communication
	IncomingHeartbeatMessage = NewIncomingMessageFromUint8Content(
		internalusbcdcenums.IncomingCategoryStatus,
		uint8(internalusbcdcenums.StatusHeartbeat),
	)

	// OutgoingStartMessage is the outgoing start message for USB-CDC communication
	OutgoingStartMessage = NewOutgoingMessageFromUint8Content(
		internalusbcdcenums.OutgoingCategoryStatus,
		uint8(internalusbcdcenums.StatusStart),
	)

	// OutgoingOKMessage is the outgoing OK message for USB-CDC communication
	OutgoingOKMessage = NewOutgoingMessageFromUint8Content(
		internalusbcdcenums.OutgoingCategoryStatus,
		uint8(internalusbcdcenums.StatusOK),
	)

	// OutgoingChallengeWithObstaclesMessage is the outgoing challenge message with obstacles
	OutgoingChallengeWithObstaclesMessage = NewOutgoingMessageFromUint8Content(
		internalusbcdcenums.OutgoingCategoryChallenge,
		uint8(internalchallengeenums.ChallengeWithObstacles),
	)

	// OutgoingChallengeWithObstaclesAndParkingMessage is the outgoing challenge message with obstacles and parking
	OutgoingChallengeWithObstaclesAndParkingMessage = NewOutgoingMessageFromUint8Content(
		internalusbcdcenums.OutgoingCategoryChallenge,
		uint8(internalchallengeenums.ChallengeWithObstaclesAndParking),
	)

	// OutgoingChallengeWithoutObstaclesMessage is the outgoing challenge message without obstacles
	OutgoingChallengeWithoutObstaclesMessage = NewOutgoingMessageFromUint8Content(
		internalusbcdcenums.OutgoingCategoryChallenge,
		uint8(internalchallengeenums.ChallengeWithoutObstacles),
	)

	// USBCDCHandler is the USB CDC handler for the Raspberry Pi Pico 2W
	USBCDCHandler Handler
)

func init() {
	usbCDCHandler, err := NewDefaultHandler(
		internalchallenge.ChallengeHandler,
		internalledonboard.OnBoardHandler,
	)
	if err != nil {
		panic(fmt.Errorf("failed to initialize usb cdc: %w", err))
	}
	USBCDCHandler = usbCDCHandler
}
