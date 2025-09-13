package usbcdc

import (
	"time"

	internalchallenge "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/challenge"
	internalledonboard "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/led/onboard"
	tinygo_types "github.com/ralvarezdev/tinygo-types"
	"github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal"
)

const (
	// EndChar is the message end character
	EndChar byte = 0x04

	// BufferSize is the size of the buffer for USB-CDC communication
	BufferSize uint8 = 8

	// ChunkSize is the default size of data chunks
	ChunkSize = 64

	// ConfirmationMessageTimeout is the timeout duration for confirmation messages
	ConfirmationMessageTimeout = time.Second * 5

	// BaudRate is the baud rate for USB-CDC communication
	BaudRate = 921600

	// IncomingMessagesBufferSize is the size of the incoming messages buffer
	IncomingMessagesBufferSize = 10
)

var (
	// IncomingStopMessage is the incoming stop message for USB-CDC communication
	IncomingStopMessage = NewIncomingStatusMessage(IncomingStatusStop)

	// IncomingOKMessage is the incoming OK message for USB-CDC communication
	IncomingOKMessage = NewIncomingStatusMessage(IncomingStatusOK)

	// IncomingHeartbeatMessage is the incoming heartbeat message for USB-CDC communication
	IncomingHeartbeatMessage = NewIncomingStatusMessage(IncomingStatusHeartbeat)

	// OutgoingStartMessage is the outgoing start message for USB-CDC communication
	OutgoingStartMessage = NewOutgoingStatusMessage(OutgoingStatusStart)

	// OutgoingOKMessage is the outgoing OK message for USB-CDC communication
	OutgoingOKMessage = NewOutgoingStatusMessage(OutgoingStatusOK)

	// OutgoingChallengeWithObstaclesMessage is the outgoing challenge message with obstacles
	OutgoingChallengeWithObstaclesMessage = NewOutgoingChallengeMessage(internalchallenge.ChallengeWithObstacles)

	// OutgoingChallengeWithObstaclesAndParkingMessage is the outgoing challenge message with obstacles and parking
	OutgoingChallengeWithObstaclesAndParkingMessage = NewOutgoingChallengeMessage(internalchallenge.ChallengeWithObstaclesAndParking)

	// OutgoingChallengeWithoutObstaclesMessage is the outgoing challenge message without obstacles
	OutgoingChallengeWithoutObstaclesMessage = NewOutgoingChallengeMessage(internalchallenge.ChallengeWithoutObstacles)

	// OutgoingDebugReceivedMotorSpeedMessage is the outgoing debug message for received motor speed
	OutgoingDebugReceivedMotorSpeedMessage = NewOutgoingDebugMessage(
		DebugReceivedMotorSpeed,
	)

	// OutgoingDebugReceivedServoAngleMessage is the outgoing debug message for received servo angle
	OutgoingDebugReceivedServoAngleMessage = NewOutgoingDebugMessage(
		DebugReceivedServoAngle,
	)

	// USBCDCHandler is the USB CDC handler for the Raspberry Pi Pico 2W
	USBCDCHandler Handler

	// failedToInitializeUSBMessage is the message printed when USB initialization fails
	failedToInitializeUSBMessage = []byte("Failed to initialize USB-CDC handler:")
)

func init() {
	usbCDCHandler, err := NewDefaultHandler(
		internalchallenge.ChallengeHandler,
		internalledonboard.OnBoardHandler,
	)
	if err != tinygo_types.ErrorCodeNil {
		internal.Logger.ErrorMessageWithErrorCode(failedToInitializeUSBMessage, err)
		return
	}
	USBCDCHandler = usbCDCHandler
}
