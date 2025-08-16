package usbcdc

import (
	"strconv"
	"time"

	"github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/challenge"
	challengeenums "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/challenge/enums"
	"github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/led"
	usbcdcenums "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/usbcdc/enums"
)

const (
	// HeaderSeparatorChar is the message header separator
	HeaderSeparatorChar uint8 = ':'

	// EndChar is the message end character
	EndChar uint8 = '\x04'

	// BufferSize is the size of the buffer for USB-CDC communication
	BufferSize uint8 = 16

	// ChunkSize is the default size of data chunks
	ChunkSize = 64

	// OutgoingMessageExpectedParts is the expected number of parts in an outgoing message
	OutgoingMessageExpectedParts = 2

	// IncomingMessageExpectedParts is the expected number of parts in an incoming message
	IncomingMessageExpectedParts = 2

	// ConfirmationMessageTimeout is the timeout duration for confirmation messages
	ConfirmationMessageTimeout = time.Second * 5
)

var (
	// HeaderSeparatorString is the string representation of the header separator character
	HeaderSeparatorString = strconv.Itoa(int(HeaderSeparatorChar))

	// OutgoingStartMessage is the outgoing start message for USB-CDC communication
	OutgoingStartMessage = NewOutgoingMessageFromUint8Content(
		usbcdcenums.OutgoingCategoryStatus,
		uint8(usbcdcenums.StatusStart),
	)

	// OutgoingOKMessage is the outgoing OK message for USB-CDC communication
	OutgoingOKMessage = NewOutgoingMessageFromUint8Content(
		usbcdcenums.OutgoingCategoryStatus,
		uint8(usbcdcenums.StatusOK),
	)

	// IncomingStopMessage is the incoming stop message for USB-CDC communication
	IncomingStopMessage = NewIncomingMessageFromUint8Content(
		usbcdcenums.IncomingCategoryStatus,
		uint8(usbcdcenums.StatusStop),
	)

	// IncomingOKMessage is the incoming OK message for USB-CDC communication
	IncomingOKMessage = NewIncomingMessageFromUint8Content(
		usbcdcenums.IncomingCategoryStatus,
		uint8(usbcdcenums.StatusOK),
	)

	// IncomingHeartbeatMessage is the incoming heartbeat message for USB-CDC communication
	IncomingHeartbeatMessage = NewIncomingMessageFromUint8Content(
		usbcdcenums.IncomingCategoryStatus,
		uint8(usbcdcenums.StatusHeartbeat),
	)

	// OutgoingChallengeWithObstaclesMessage is the outgoing challenge message with obstacles
	OutgoingChallengeWithObstaclesMessage = NewOutgoingMessageFromUint8Content(
		usbcdcenums.OutgoingCategoryChallenge,
		uint8(challengeenums.ChallengeWithObstacles),
	)

	// OutgoingChallengeWithObstaclesAndParkingMessage is the outgoing challenge message with obstacles and parking
	OutgoingChallengeWithObstaclesAndParkingMessage = NewOutgoingMessageFromUint8Content(
		usbcdcenums.OutgoingCategoryChallenge,
		uint8(challengeenums.ChallengeWithObstaclesAndParking),
	)

	// OutgoingChallengeWithoutObstaclesMessage is the outgoing challenge message without obstacles
	OutgoingChallengeWithoutObstaclesMessage = NewOutgoingMessageFromUint8Content(
		usbcdcenums.OutgoingCategoryChallenge,
		uint8(challengeenums.ChallengeWithoutObstacles),
	)

	// USBCDCHandler is the USB CDC handler for the Raspberry Pi Pico 2W
	USBCDCHandler, _ = NewDefaultHandler(
		challenge.ChallengeHandler,
		led.OnBoardLEDHandler,
	)
)
