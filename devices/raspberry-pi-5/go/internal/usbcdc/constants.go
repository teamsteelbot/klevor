package usbcdc

import (
	"time"

	"github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal"
	tinygoerrors "github.com/ralvarezdev/tinygo-errors"
)

const (
	// ConfirmationMessageTimeout is the timeout duration for confirmation messages
	ConfirmationMessageTimeout = time.Second * 5

	// StartAndEndByte is the message start and end character
	StartAndEndByte uint8 = 0x7E

	// ControlByte is the control character
	ControlByte uint8 = 0x7D

	// XORByte is the XOR character
	XORByte uint8 = 0x20

	// ErrorCodeChallengeStartNumber is the starting number for challenge-related error codes.
	ErrorCodeChallengeStartNumber uint16 = 1

	// ErrorCodeCyw43439StartNumber is the starting number for CYW43439-related error codes.
	ErrorCodeCyw43439StartNumber uint16 = 10

	// ErrorCodeLEDStartNumber is the starting number for LED-related error codes.
	ErrorCodeLEDStartNumber uint16 = 20

	// ErrorCodeMovementStartNumber is the starting number for movement-related error codes.
	ErrorCodeMovementStartNumber uint16 = 30

	// ErrorCodeSwitchStartNumber is the starting number for switch-related error codes.
	ErrorCodeSwitchStartNumber uint16 = 40

	// ErrorCodeUSBCDCStartNumber is the starting number for USB CDC-related error codes.
	ErrorCodeUSBCDCStartNumber uint16 = 50
)


const (
	ErrorCodeChallengeNilHandler tinygoerrors.ErrorCode = tinygoerrors.ErrorCode(iota + ErrorCodeChallengeStartNumber)
	ErrorCodeChallengeNilObstaclesPullUpHandler
	ErrorCodeChallengeNilParkingPullUpHandler
	ErrorCodeChallengeInvalidChallengeUint8
)

const (
	ErrorCodeCyw43439NilDevice tinygoerrors.ErrorCode = tinygoerrors.ErrorCode(iota + ErrorCodeCyw43439StartNumber)
	ErrorCodeCyw43439FailedToInitialize
)

const (
	ErrorCodeLEDNilHandler tinygoerrors.ErrorCode = tinygoerrors.ErrorCode(iota + ErrorCodeLEDStartNumber)
	ErrorCodeLEDNegativeBlinkCount
	ErrorCodeLEDNegativeDelayDuration
)

const (
	ErrorCodeMovementNilHandler tinygoerrors.ErrorCode = tinygoerrors.ErrorCode(iota + ErrorCodeMovementStartNumber)
)

const (
	ErrorCodeSwitchNilOnEventFunction tinygoerrors.ErrorCode = tinygoerrors.ErrorCode(iota + ErrorCodeSwitchStartNumber)
)

const (
	ErrorCodeUSBCDCNilHandler tinygoerrors.ErrorCode = tinygoerrors.ErrorCode(iota + ErrorCodeUSBCDCStartNumber)
	ErrorCodeUSBCDCNilOutgoingCategory
	ErrorCodeUSBCDCUnknownOutgoingCategory
	ErrorCodeUSBCDCNilIncomingCategory
	ErrorCodeUSBCDCUnknownIncomingCategory
	ErrorCodeUSBCDCInvalidMaxMessageDataLength
	ErrorCodeUSBCDCFailedToSendStartByte
	ErrorCodeUSBCDCFailedToSendOutgoingCategory
	ErrorCodeUSBCDCFailedToSendControlByte
	ErrorCodeUSBCDCFailedToSendMessageContent
	ErrorCodeUSBCDCFailedToSendEndByte
	ErrorCodeUSBCDCBufferTooShortForRawFloat64
	ErrorCodeUSBCDCUnknownQuaternionIndex
	ErrorCodeUSBCDCUnknownEulerDegreesIndex
	ErrorCodeUSBCDCUnknownIncomingStatus
	ErrorCodeUSBCDCUnknownOutgoingStatus
	ErrorCodeUSBCDCUnknownChallenge
	ErrorCodeUSBCDCBufferTooShortForRawUint16
	ErrorCodeUSBCDCBufferTooShortForRawUint8
	ErrorCodeUSBCDCConfirmationMessageTimeout
	ErrorCodeUSBCDCReadByteTimeout
	ErrorCodeUSBCDCFailedReadingFromSerial
	ErrorCodeUSBCDCFailedToConfigureUSBCDC
	ErrorCodeUSBCDCFailedToSendInitializationMessage
	ErrorCodeUSBCDCInvalidIncomingMessageDataLength
	ErrorCodeUSBCDCInvalidOutgoingMessageDataLength
	ErrorCodeUSBCDCReadMessageTimeout
	ErrorCodeUSBCDCReceivedUnexpectedConfirmationMessage
	ErrorCodeUSBCDCFailedToSendChecksumByte
	ErrorCodeUSBCDCInvalidChecksum
)

var (
	// StartAndEndBytes is the byte slice for the start and end character
	StartAndEndBytes = []byte{StartAndEndByte}

	// ReadTimeout is the timeout duration for reading from the USB-CDC port
	ReadTimeout = time.Second * 2

	// StopTimeout is the timeout duration for stopping the USB-CDC communication
	StopTimeout = 3 * time.Second

	// HeartbeatInterval is the interval for sending heartbeat messages
	HeartbeatInterval = 1 * time.Second

	// BufferSize is the size of the buffer for USB-CDC communication
	BufferSize uint8 = 64

	// BaudRate is the baud rate for USB-CDC communication
	BaudRate = 921600

	// HandlerLoggerProducerTag is the logger producer tag for USB-CDC handler
	HandlerLoggerProducerTag = "USB_CDC_HANDLER"

	// IncomingMessagesLoggerProducerTag is the logger producer tag for incoming messages processing
	IncomingMessagesLoggerProducerTag = "USB_CDC_INCOMING_MESSAGES"

	// OutgoingMessagesLoggerProducerTag is the logger producer tag for outgoing messages processing
	OutgoingMessagesLoggerProducerTag = "USB_CDC_OUTGOING_MESSAGES"

	// OutgoingMessagesChannelBufferSize is the size of the outgoing messages channel buffer
	OutgoingMessagesChannelBufferSize = 100

	// OutgoingStopMessage is the outgoing stop message for USB-CDC communication
	OutgoingStopMessage = NewOutgoingStatusMessage(OutgoingStatusStop)

	// OutgoingOKMessage is the outgoing OK message for USB-CDC communication
	OutgoingOKMessage = NewOutgoingStatusMessage(OutgoingStatusOK)

	// OutgoingHeartbeatMessage is the outgoing heartbeat message for USB-CDC communication
	OutgoingHeartbeatMessage = NewOutgoingStatusMessage(OutgoingStatusHeartbeat)

	// QuaternionXIndex is the index for the quaternion X component
	QuaternionXIndex = 0
	
	// QuaternionYIndex is the index for the quaternion Y component
	QuaternionYIndex = 1
	
	// QuaternionZIndex is the index for the quaternion Z component
	QuaternionZIndex = 2

	// QuaternionWIndex is the index for the quaternion W component
	QuaternionWIndex = 3

	// EulerDegreesRollIndex is the index for the Euler degrees roll component
	EulerDegreesRollIndex = 0

	// EulerDegreesRollMinValue is the minimum value for the Euler degrees roll component
	EulerDegreesRollMinValue = -180.0
	
	// EulerDegreesRollMaxValue is the maximum value for the Euler degrees roll component
	EulerDegreesRollMaxValue = 180.0

	// EulerDegreesPitchIndex is the index for the Euler degrees pitch component
	EulerDegreesPitchIndex = 1

	// EulerDegreesPitchMinValue is the minimum value for the Euler degrees pitch component
	EulerDegreesPitchMinValue = -90.0

	// EulerDegreesPitchMaxValue is the maximum value for the Euler degrees pitch component
	EulerDegreesPitchMaxValue = 90.0

	// EulerDegreesYawIndex is the index for the Euler degrees yaw component
	EulerDegreesYawIndex = 2

	// EulerDegreesYawMinValue is the minimum value for the Euler degrees yaw component
	EulerDegreesYawMinValue = -180.0

	// EulerDegreesYawMaxValue is the maximum value for the Euler degrees yaw component
	EulerDegreesYawMaxValue = 180.0

	// OutgoingMotorSpeedStopMessage is the outgoing motor speed stop message for USB-CDC communication
	OutgoingMotorSpeedStopMessage = NewOutgoingMessage(
		OutgoingCategoryMotorSpeedStop,
		[]byte{},
	)

	// OutgoingServoDirectionCenterMessage is the outgoing servo direction center message for USB-CDC communication
	OutgoingServoDirectionCenterMessage = NewOutgoingMessage(
		OutgoingCategoryServoDirectionCenter,
		[]byte{},
	)

	// OutgoingGetMaxMotorSpeedValueMessage is the outgoing message to request the maximum motor speed value
	OutgoingGetMaxMotorSpeedValueMessage = NewOutgoingMessage(
		OutgoingCategoryGetMaxMotorSpeedValue,
		[]byte{},
	)

	// OutgoingGetMaxServoDirectionValueMessage is the outgoing message to request the maximum servo direction value
	OutgoingGetMaxServoDirectionValueMessage = NewOutgoingMessage(
		OutgoingCategoryGetMaxServoDirectionValue,
		[]byte{},
	)

	// IncomingStartMessage is the incoming start message for USB-CDC communication
	IncomingStartMessage = NewIncomingStatusMessage(IncomingStatusStart)

	// IncomingOKMessage is the incoming OK message for USB-CDC communication
	IncomingOKMessage = NewIncomingStatusMessage(IncomingStatusOK)

	// IncomingChallengeWithObstaclesMessage is the incoming challenge message with obstacles
	IncomingChallengeWithObstaclesMessage = NewIncomingChallengeMessage(internal.ChallengeWithObstacles)

	// IncomingChallengeWithObstaclesAndParkingMessage is the incoming challenge message with obstacles and parking
	IncomingChallengeWithObstaclesAndParkingMessage = NewIncomingChallengeMessage(internal.ChallengeWithObstaclesAndParking)

	// IncomingChallengeWithoutObstaclesMessage is the incoming challenge message without obstacles
	IncomingChallengeWithoutObstaclesMessage = NewIncomingChallengeMessage(internal.ChallengeWithoutObstacles)

	// ErrorCodeMessages maps error codes to their corresponding error messages.
	ErrorCodeMessages = map[tinygoerrors.ErrorCode]string{
		// Challenge errors
		ErrorCodeChallengeNilHandler:                "challenge handler cannot be nil",
		ErrorCodeChallengeNilObstaclesPullUpHandler: "challenge obstacles pull-up handler cannot be nil",
		ErrorCodeChallengeNilParkingPullUpHandler:   "challenge parking pull-up handler cannot be nil",
		ErrorCodeChallengeInvalidChallengeUint8:     "invalid challenge uint8",

		// Cyw43439 errors
		ErrorCodeCyw43439NilDevice:          "cyw43439 device cannot be nil",
		ErrorCodeCyw43439FailedToInitialize: "cyw43439 failed to initialize",

		// LED errors
		ErrorCodeLEDNilHandler:            "led handler cannot be nil",
		ErrorCodeLEDNegativeBlinkCount:    "led blink count cannot be negative",
		ErrorCodeLEDNegativeDelayDuration: "led delay duration cannot be negative",

		// Movement errors
		ErrorCodeMovementNilHandler: "movement handler cannot be nil",

		// Switch errors
		ErrorCodeSwitchNilOnEventFunction: "switch onevent function cannot be nil",

		// USB CDC errors
		ErrorCodeUSBCDCNilHandler:                            "usb-cdc handler cannot be nil",
		ErrorCodeUSBCDCNilOutgoingCategory:                   "usb-cdc outgoing category cannot be nil",
		ErrorCodeUSBCDCUnknownOutgoingCategory:               "usb-cdc unknown outgoing category",
		ErrorCodeUSBCDCNilIncomingCategory:                   "usb-cdc incoming category cannot be nil",
		ErrorCodeUSBCDCUnknownIncomingCategory:               "usb-cdc unknown incoming category",
		ErrorCodeUSBCDCInvalidMaxMessageDataLength:           "usb-cdc invalid max message data length",
		ErrorCodeUSBCDCFailedToSendStartByte:            "usb-cdc failed to send start byte",
		ErrorCodeUSBCDCFailedToSendOutgoingCategory:          "usb-cdc failed to send outgoing category",
		ErrorCodeUSBCDCFailedToSendControlByte:          "usb-cdc failed to send control byte",
		ErrorCodeUSBCDCFailedToSendMessageContent:            "usb-cdc failed to send message content",
		ErrorCodeUSBCDCFailedToSendEndByte:              "usb-cdc failed to send end byte",
		ErrorCodeUSBCDCBufferTooShortForRawFloat64:           "usb-cdc buffer too short for raw float64",
		ErrorCodeUSBCDCUnknownQuaternionIndex:                "usb-cdc unknown quaternion index",
		ErrorCodeUSBCDCUnknownEulerDegreesIndex:              "usb-cdc unknown euler degrees index",
		ErrorCodeUSBCDCUnknownIncomingStatus:                 "usb-cdc unknown incoming status",
		ErrorCodeUSBCDCUnknownOutgoingStatus:                 "usb-cdc unknown outgoing status",
		ErrorCodeUSBCDCUnknownChallenge:                      "usb-cdc unknown challenge",
		ErrorCodeUSBCDCBufferTooShortForRawUint16:            "usb-cdc buffer too short for raw uint16",
		ErrorCodeUSBCDCBufferTooShortForRawUint8:             "usb-cdc buffer too short for raw uint8",
		ErrorCodeUSBCDCConfirmationMessageTimeout:            "usb-cdc confirmation message timeout",
		ErrorCodeUSBCDCReadByteTimeout:                       "usb-cdc read byte timeout",
		ErrorCodeUSBCDCFailedReadingFromSerial:               "usb-cdc failed reading from serial",
		ErrorCodeUSBCDCFailedToConfigureUSBCDC:               "usb-cdc failed to configure",
		ErrorCodeUSBCDCFailedToSendInitializationMessage:     "usb-cdc failed to send initialization message",
		ErrorCodeUSBCDCInvalidIncomingMessageDataLength:      "usb-cdc invalid incoming message data length",
		ErrorCodeUSBCDCInvalidOutgoingMessageDataLength:      "usb-cdc invalid outgoing message data length",
		ErrorCodeUSBCDCReadMessageTimeout:                    "usb-cdc read message timeout",
		ErrorCodeUSBCDCReceivedUnexpectedConfirmationMessage: "usb-cdc received unexpected confirmation message",
		ErrorCodeUSBCDCFailedToSendChecksumByte:              "usb-cdc failed to send checksum byte",
		ErrorCodeUSBCDCInvalidChecksum:                        "usb-cdc invalid checksum",
	}
)
