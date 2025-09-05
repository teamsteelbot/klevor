package usbcdc

import (
	"time"

	"github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal"
	internalusbcdcenums "github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal/usbcdc/enums"
)

const (
	// EndChar is the message end character
	EndChar byte = 0x04

	// InitializationMessage is the initialization message sent by the Raspberry Pi Pico 2W
	InitializationMessage = EndChar
)

var (
	// ReadTimeout is the timeout duration for reading from the USB-CDC port
	ReadTimeout = time.Second * 2

	// StopTimeout is the timeout duration for stopping the USB-CDC communication
	StopTimeout = 5 * time.Second

	// HeartbeatInterval is the interval for sending heartbeat messages
	HeartbeatInterval = 1 * time.Second

	// BufferSize is the size of the buffer for USB-CDC communication
	BufferSize uint8 = 64

	// BaudRate is the baud rate for USB-CDC communication
	BaudRate = 921600

	// HandlerLoggerProducerTag is the logger producer tag for USB-CDC handler
	HandlerLoggerProducerTag = "USB_CDC_HANDLER"

	// OutgoingMessagesChannelBufferSize is the size of the outgoing messages channel buffer
	OutgoingMessagesChannelBufferSize = 100

	// OutgoingStopMessage is the outgoing stop message for USB-CDC communication
	OutgoingStopMessage = NewOutgoingStatusMessage(internalusbcdcenums.OutgoingStatusStop)

	// OutgoingOKMessage is the outgoing OK message for USB-CDC communication
	OutgoingOKMessage = NewOutgoingStatusMessage(internalusbcdcenums.OutgoingStatusOK)

	// OutgoingHeartbeatMessage is the outgoing heartbeat message for USB-CDC communication
	OutgoingHeartbeatMessage = NewOutgoingStatusMessage(internalusbcdcenums.OutgoingStatusHeartbeat)

	// OutgoingMotorSpeedStopMessage is the outgoing motor speed stop message for USB-CDC communication
	OutgoingMotorSpeedStopMessage = NewOutgoingMessage(
		internalusbcdcenums.OutgoingCategoryMotorSpeedStop,
		"",
	)

	// OutgoingServoDirectionCenterMessage is the outgoing servo direction center message for USB-CDC communication
	OutgoingServoDirectionCenterMessage = NewOutgoingMessage(
		internalusbcdcenums.OutgoingCategoryServoDirectionCenter,
		"",
	)

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
