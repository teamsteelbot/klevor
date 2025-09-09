package usbcdc

import (
	"errors"
	
	tinygotypes "github.com/ralvarezdev/tinygo-types"
)

const (
	// ErrorCodeGeneralStartNumber is the starting number for general error codes.
	ErrorCodeGeneralStartNumber uint16 = 1

	// ErrorCodeChallengeStartNumber is the starting number for challenge-related error codes.
	ErrorCodeChallengeStartNumber uint16 = 100

	// ErrorCodeCyw43439StartNumber is the starting number for CYW43439-related error codes.
	ErrorCodeCyw43439StartNumber uint16 = 200

	// ErrorCodeDebugStartNumber is the starting number for debug-related error codes.
	ErrorCodeDebugStartNumber uint16 = 300

	// ErrorCodeESCMotorStartNumber is the starting number for ESC motor-related error codes.
	ErrorCodeESCMotorStartNumber uint16 = 400

	// ErrorCodeLEDStartNumber is the starting number for LED-related error codes.
	ErrorCodeLEDStartNumber uint16 = 500

	// ErrorCodeMovementStartNumber is the starting number for movement-related error codes.
	ErrorCodeMovementStartNumber uint16 = 600

	// ErrorCodePullUpResistorStartNumber is the starting number for pull-up resistor-related error codes.
	ErrorCodePullUpResistorStartNumber uint16 = 700

	// ErrorCodeServoStartNumber is the starting number for servo-related error codes.
	ErrorCodeServoStartNumber uint16 = 800

	// ErrorCodeSwitchStartNumber is the starting number for switch-related error codes.
	ErrorCodeSwitchStartNumber uint16 = 900

	// ErrorCodeUSBCDCStartNumber is the starting number for USB CDC-related error codes.
	ErrorCodeUSBCDCStartNumber uint16 = 1000

	// ErrorCodeBNO08XStartNumber is the starting number for BNO08X-related error codes.
	ErrorCodeBNO08XStartNumber uint16 = 5000
)

const (
	ErrorCodeFailedToConfigurePWM tinygotypes.ErrorCode = tinygotypes.ErrorCode(iota + ErrorCodeGeneralStartNumber)
)

const (
	ErrorCodeChallengeNilHandler tinygotypes.ErrorCode = tinygotypes.ErrorCode(iota + ErrorCodeChallengeStartNumber)
	ErrorCodeChallengeNilObstaclesPullUpHandler
	ErrorCodeChallengeNilParkingPullUpHandler
	ErrorCodeChallengeInvalidChallengeUint8
)

const (
	ErrorCodeCyw43439NilDevice tinygotypes.ErrorCode = tinygotypes.ErrorCode(iota + ErrorCodeCyw43439StartNumber)
)

const (
	ErrorCodeDebugNilHandler tinygotypes.ErrorCode = tinygotypes.ErrorCode(iota + ErrorCodeDebugStartNumber)
)

const (
	ErrorCodeESCMotorNilOptions tinygotypes.ErrorCode = tinygotypes.ErrorCode(iota + ErrorCodeESCMotorStartNumber)
	ErrorCodeESCMotorFailedToInitializeServo
	ErrorCodeESCMotorInvalidMotorSpeedValue
	ErrorCodeESCMotorSpeedOutOfRange
	ErrorCodeESCMotorSpeedBelowMinPulseWidth
	ErrorCodeESCMotorSpeedAboveMaxPulseWidth
	ErrorCodeESCMotorFailedToSendDebugMotorSpeedMessage
	ErrorCodeESCMotorUnknownMotorSpeedCategory
)

const (
	ErrorCodeLEDNilHandler tinygotypes.ErrorCode = tinygotypes.ErrorCode(iota + ErrorCodeLEDStartNumber)
	ErrorCodeLEDNegativeBlinkCount
	ErrorCodeLEDNegativeDelayDuration
)

const (
	ErrorCodeMovementNilHandler tinygotypes.ErrorCode = tinygotypes.ErrorCode(iota + ErrorCodeMovementStartNumber)
)

const (
	ErrorCodePullUpResistorNilHandler = tinygotypes.ErrorCode(iota + ErrorCodePullUpResistorStartNumber)
)

const (
	ErrorCodeServoNilOptions tinygotypes.ErrorCode = tinygotypes.ErrorCode(iota + ErrorCodeServoStartNumber)
	ErrorCodeServoFailedToInitializeServo 
	ErrorCodeServoInvalidAngleValue
	ErrorCodeServoAngleOutOfRange
	ErrorCodeServoAngleBelowMinPulseWidth
	ErrorCodeServoAngleAboveMaxPulseWidth
	ErrorCodeServoFailedToSendDebugServoAngleMessage
	ErrorCodeServoUnknownAngleCategory
	ErrorCodeServoFailedToSetServoAngle
)

const (
	ErrorCodeSwitchNilOnEventFunction tinygotypes.ErrorCode = tinygotypes.ErrorCode(iota + ErrorCodeSwitchStartNumber)
)

const (
	ErrorCodeUSBCDCNilHandler tinygotypes.ErrorCode = tinygotypes.ErrorCode(iota + ErrorCodeUSBCDCStartNumber)
	ErrorCodeUSBCDCNilOutgoingMessage
	ErrorCodeUSBCDCNilIncomingMessage
	ErrorCodeUSBCDCConfirmationMessageTimeout
	ErrorCodeUSBCDCUnknownChallengeType
	ErrorCodeUSBCDCFailedReadingFromSerial
	ErrorCodeUSBCDCNilOutgoingCategory
	ErrorCodeUSBCDCFailedToSendChunkMessage
	ErrorCodeUSBCDCFailedToSendMessage
	ErrorCodeUSBCDCFailedToSendEndCharacter
	ErrorCodeUSBCDCFailedToConfigureUSBCDC
	ErrorCodeUSBCDCInvalidIncomingCategoryUint8
	ErrorCodeUSBCDCInvalidOutgoingCategoryString
	ErrorCodeUSBCDCInvalidOutgoingCategoryUint8
	ErrorCodeUSBCDCInvalidIncomingStatusUint8
	ErrorCodeUSBCDCInvalidOutgoingStatusUint8
	ErrorCodeUSBCDCInvalidDebugUint8
	ErrorCodeUSBCDCIncomingMessageEmptyContent
	ErrorCodeUSBCDCEmptyIncomingMessageBuffer
	ErrorCodeUSBCDCInvalidIncomingMessageContentUint16
	ErrorCodeUSBCDCInvalidIncomingMessageMissingEndCharacter
)

var (
	// ErrorCodeMessages is a map of error codes to their messages.
	ErrorCodeMessages = map[tinygotypes.ErrorCode]string{
		ErrorCodeFailedToConfigurePWM: "failed to configure pwm",
		ErrorCodeChallengeNilHandler:   "challenge handler cannot be nil",
		ErrorCodeChallengeNilObstaclesPullUpHandler: "challenge obstacles pull-up handler cannot be nil",
		ErrorCodeChallengeNilParkingPullUpHandler:   "challenge parking pull-up handler cannot be nil",
		ErrorCodeChallengeInvalidChallengeUint8:     "invalid challenge uint8",
		ErrorCodeCyw43439NilDevice:    "cyw43439 device cannot be nil",
		ErrorCodeDebugNilHandler:      "debug handler cannot be nil",
		ErrorCodeESCMotorNilOptions:   "esc motor options cannot be nil",
		ErrorCodeESCMotorFailedToInitializeServo: "failed to initialize esc motor servo",
		ErrorCodeESCMotorInvalidMotorSpeedValue: "invalid motor speed value",
		ErrorCodeESCMotorSpeedOutOfRange:                       "esc motor speed out of range",
		ErrorCodeESCMotorSpeedBelowMinPulseWidth:               "esc motor speed below min pulse width",
		ErrorCodeESCMotorSpeedAboveMaxPulseWidth:               "esc motor speed above max pulse width",
		ErrorCodeESCMotorFailedToSendDebugMotorSpeedMessage:    "failed to send debug motor speed message",
		ErrorCodeESCMotorUnknownMotorSpeedCategory:               "unknown motor speed category",
		ErrorCodeLEDNilHandler:                               "led handler cannot be nil",
		ErrorCodeLEDNegativeBlinkCount:                       "times cannot be negative",
		ErrorCodeLEDNegativeDelayDuration:                    "delay cannot be negative",
		ErrorCodeMovementNilHandler:                            "movement handler cannot be nil",
		ErrorCodePullUpResistorNilHandler:                           "pull-up handler cannot be nil",
		ErrorCodeServoNilOptions:                               "servo options cannot be nil",
		ErrorCodeServoFailedToInitializeServo:                 "failed to initialize servo",
		ErrorCodeServoInvalidAngleValue:                        "invalid servo angle value",
		ErrorCodeServoAngleOutOfRange:                          "servo angle out of range",
		ErrorCodeServoAngleBelowMinPulseWidth:                  "servo angle below min pulse width",
		ErrorCodeServoAngleAboveMaxPulseWidth:                  "servo angle above max pulse width",
		ErrorCodeServoFailedToSendDebugServoAngleMessage:       "failed to send debug servo angle message",
		ErrorCodeServoUnknownAngleCategory:                     "unknown servo angle category",
		ErrorCodeServoFailedToSetServoAngle:                    "failed to set servo angle",
		ErrorCodeSwitchNilOnEventFunction:                     "onEvent function cannot be nil",
		ErrorCodeUSBCDCNilHandler:                               "usb-cdc handler cannot be nil",
		ErrorCodeUSBCDCNilOutgoingMessage:                       "outgoing message cannot be nil",
		ErrorCodeUSBCDCNilIncomingMessage:                       "incoming message cannot be nil",
		ErrorCodeUSBCDCConfirmationMessageTimeout:               "confirmation message timeout exceeded for message",
		ErrorCodeUSBCDCUnknownChallengeType:                     "unknown challenge type",
		ErrorCodeUSBCDCFailedReadingFromSerial:                  "failed reading from serial",
		ErrorCodeUSBCDCNilOutgoingCategory:                      "outgoing message category cannot be nil or empty",
		ErrorCodeUSBCDCFailedToSendChunkMessage:                 "failed to send chunk message",
		ErrorCodeUSBCDCFailedToSendMessage:                      "failed to send message",
		ErrorCodeUSBCDCFailedToSendEndCharacter:                 "failed to send end character",
		ErrorCodeUSBCDCFailedToConfigureUSBCDC:                  "failed to configure USB CDC",
		ErrorCodeUSBCDCInvalidIncomingCategoryUint8:             "invalid incoming category uint8",
		ErrorCodeUSBCDCInvalidOutgoingCategoryString:            "invalid outgoing category string",
		ErrorCodeUSBCDCInvalidOutgoingCategoryUint8:             "invalid outgoing category uint8",
		ErrorCodeUSBCDCInvalidIncomingStatusUint8:               "invalid incoming status uint8",
		ErrorCodeUSBCDCInvalidOutgoingStatusUint8:               "invalid outgoing status uint8",
		ErrorCodeUSBCDCInvalidDebugUint8:                       "invalid debug uint8",
		ErrorCodeUSBCDCIncomingMessageEmptyContent:            "incoming message has empty content",
		ErrorCodeUSBCDCEmptyIncomingMessageBuffer:             "incoming message buffer is empty",
		ErrorCodeUSBCDCInvalidIncomingMessageContentUint16:    "invalid incoming message content uint16",
		ErrorCodeUSBCDCInvalidIncomingMessageMissingEndCharacter: "invalid incoming message: missing end character",
	}
)

var (
	ErrNilHandler                               = errors.New("handler cannot be nil")
	ErrNilBuffer                                = errors.New("buffer cannot be nil")
	ErrHandlerAlreadyRunning                    = errors.New("handler is already running")
	ErrFailedToListPorts                        = errors.New("failed to list ports")
	ErrNoPortsFound                             = errors.New("no ports found")
	ErrPortNotFound                             = errors.New("port not found")
	ErrNilSendFunction                          = errors.New("nil send function")
	ErrNilCloseFunction                         = errors.New("nil close function")
	ErrSenderAlreadyClosed                      = errors.New("sender is already closed")
	ErrHandlerClosed                            = errors.New("handler is closed")
	ErrOutgoingMessagesChannelClosedAheadOfTime = errors.New("outgoing messages channel closed ahead of time")
	ErrIncomingMessageWithoutContent            = errors.New("incoming message without content")
)
