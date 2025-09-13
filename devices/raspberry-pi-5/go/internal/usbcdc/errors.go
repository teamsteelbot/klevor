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
	ErrorCodeUSBCDCNilQuaternion
	ErrorCodeUSBCDCNilIncomingMessageBuffer
	ErrorCodeUSBCDCFailedToSendInitializationMessage
)

const (
	ErrorCodeBNO08XPacketBufferIndexOutOfRange tinygotypes.ErrorCode = tinygotypes.ErrorCode(iota + ErrorCodeBNO08XStartNumber)
	ErrorCodeBNO08XInvalidChannelNumber
	ErrorCodeBNO08XNilPacketReader
	ErrorCodeBNO08XNilPacketWriter
	ErrorCodeBNO08XNilUARTBus
	ErrorCodeBNO08XFailedToConfigureUART
	ErrorCodeBNO08XFailedToResetUARTRVC
	ErrorCodeBNO08XUARTRVCNilFrame
	ErrorCodeBNO08XUARTRVCFrameTooShort
	ErrorCodeBNO08XUARTRVCInvalidChecksum
	ErrorCodeBNO08XUARTRVCByteTimeout
	ErrorCodeBNO08XUARTRVCFailedToReadByte
	ErrorCodeBNO08XFailedToParseFrame
	ErrorCodeBNO08XUARTRVCUARTTimeout
	ErrorCodeBNO08XFailedToCreatePacket
	ErrorCodeBNO08XFailedToSetUARTFormat
	ErrorCodeBNO08XFailedToCreatePacketReader
	ErrorCodeBNO08XFailedToCreatePacketWriter
	ErrorCodeBNO08XUARTByteTimeout
	ErrorCodeBNO08XUARTFailedToReadByte
	ErrorCodeBNO08XFailedToResetBNO08X
	ErrorCodeBNO08XNilPacketBuffer
	ErrorCodeBNO08XFailedToGetExpectedReportLength
	ErrorCodeBNO08XInvalidReportLength
	ErrorCodeBNO08XFailedToGetReportID
	ErrorCodeBNO08XInsertCommandRequestReportBufferTooShort
	ErrorCodeBNO08XInsertCommandRequestReportTooManyArguments
	ErrorCodeBNO08XUnknownReportID
	ErrorCodeBNO08XFailedToCreatePacketFromBuffer
	ErrorCodeBNO08XFailedToCreateReportFromPacketBuffer
	ErrorCodeBNO08XInvalidReportIDToParseReport
	ErrorCodeBNO08XInvalidReportStabilityClassificationUint8
	ErrorCodeBNO08XInvalidReportActivityUint8
	ErrorCodeBNO08XInvalidReportIDForFourDimensionalParsing
	ErrorCodeBNO08XInvalidReportIDForThreeDimensionalParsing
	ErrorCodeBNO08XInvalidReportAccuracyStatusUint8
	ErrorCodeBNO08XSensorReportDataTooShort
	ErrorCodeBNO08XNoPacketAvailable
	ErrorCodeBNO08XInvalidReportDataLength
	ErrorCodeBNO08XUARTEndMissing
	ErrorCodeBNO08XPacketHeaderBufferTooShort
	ErrorCodeBNO08XNilDestinationBuffer
	ErrorCodeBNO08XInvalidStartOrEndIndex
	ErrorCodeBNO08XNilPacketData
	ErrorCodeBNO08XCommandRequestReportNilBuffer
	ErrorCodeBNO08XNilReportData
	ErrorCodeBNO08XNilCommandRequestReportParameters
	ErrorCodeBNO08XPacketDataTooShort
	ErrorCodeBNO08XI2CFailedToProbeDevice
	ErrorCodeBNO08XI2CFailedToProbeDeviceRepeatly
	ErrorCodeBNO08XNilI2CBus
	ErrorCodeBNO08XInvalidI2CAddress
	ErrorCodeBNO08XFailedToConfigureI2C
	ErrorCodeBNO08XI2CFailedToWritePacketHeaderBuffer
	ErrorCodeBNO08XI2CFailedToWritePacketPacketBuffer
	ErrorCodeBNO08XPacketBufferTooShortForPacketHeader
	ErrorCodeBNO08XPacketBufferTooShortForPacket
	ErrorCodeBNO08XI2CFailedToReadRequestedDataLength
	ErrorCodeBNO08XInvalidPacketSize
	ErrorCodeBNO08XNilSPIBus
	ErrorCodeBNO08XFailedToConfigureSPI
	ErrorCodeBNO08XFailedToWakeUpSPI
	ErrorCodeBNO08XSPIFailedToWritePacketHeaderBuffer
	ErrorCodeBNO08XSPIFailedToWritePacketPacketBuffer
	ErrorCodeBNO08XSPIFailedToReadRequestedDataLength
	ErrorCodeBNO08XFailedToEnableDependencyFeature
	ErrorCodeBNO08XFailedToEnableFeature
	ErrorCodeBNO08XFailedToBeginCalibration
	ErrorCodeBNO08XNilSubcommandParams
	ErrorCodeBNO08XFailedToInsertCommandRequestReport
	ErrorCodeBNO08XFailedToSendMeCommandRequestPacket
	ErrorCodeBNO08XFailedToSendCommandRequestPacketToSaveCalibrationData
	ErrorCodeBNO08XFailedToSaveCalibrationData
	ErrorCodeBNO08XFailedToSendResetCommandRequestPacket
	ErrorCodeBNO08XFailedToReadSensorID
	ErrorCodeBNO08XFailedToSendProductIDRequestPacket
	ErrorCodeBNO08XWaitingForPacketTimedOut
	ErrorCodeBNO08XMismatchedPacketDataLength
	ErrorCodeBNO08XFailedToSaveDynamicCalibrationData
	ErrorCodeBNO08XFailedToParseGetFeatureReport
	ErrorCodeBNO08XFailedToParseSensorID
	ErrorCodeBNO08XFailedToParseRawMagnetometerReport
	ErrorCodeBNO08XFailedToParseStepCounterReport
	ErrorCodeBNO08XFailedToParseShakeReport
	ErrorCodeBNO08XFailedToParseStabilityClassifierReport
	ErrorCodeBNO08XFailedToParseActivityClassifierReport
	ErrorCodeBNO08XFailedToParseMagnetometerReport
	ErrorCodeBNO08XFailedToParseRotationVectorReport
	ErrorCodeBNO08XFailedToParseGeomagneticRotationVectorReport
	ErrorCodeBNO08XFailedToParseGameRotationVectorReport
	ErrorCodeBNO08XFailedToParseAccelerometerReport
	ErrorCodeBNO08XFailedToParseLinearAccelerationReport
	ErrorCodeBNO08XFailedToParseGravityReport
	ErrorCodeBNO08XFailedToParseGyroscopeReport
	ErrorCodeBNO08XFailedToParseRawGyroscopeReport
	ErrorCodeBNO08XFailedToParseRawAccelerometerReport
	ErrorCodeBNO08XFailedToGetReportLengthForTheGivenReportID
	ErrorCodeBNO08XUnprocessableBatchBytes
	ErrorCodeBNO08XI2CFailedToReadPacketHeader
	ErrorCodeBNO08XSPIFailedToReadPacketHeader
	ErrorCodeBNO08XUnhandledUARTControlSHTPProtocol
	ErrorCodeBNO08XNilBNO08XInstance
	ErrorCodeBNO08XSetFeatureEnableReportDataNilBuffer
	ErrorCodeBNO08XSetFeatureEnableReportDataBufferTooShort
	ErrorCodeBNO08XNilPacketHeaderBuffer
	ErrorCodeBNO08XReportHeaderBufferTooShort
	ErrorCodeBNO08XNilWaitForPacketFunction
	ErrorCodeBNO08XInvalidMode
	ErrorCodeBNO08XUnknownModeAttemptingSoftwareReset
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
		ErrorCodeUSBCDCNilQuaternion:                          "nil quaternion provided",
		ErrorCodeUSBCDCNilIncomingMessageBuffer:               "incoming message buffer cannot be nil",
		ErrorCodeUSBCDCFailedToSendInitializationMessage:      "failed to send initialization message",
		ErrorCodeBNO08XPacketBufferIndexOutOfRange:            "bno08x packet buffer index out of range",
		ErrorCodeBNO08XInvalidChannelNumber:                   "bno08x invalid channel number",
		ErrorCodeBNO08XNilPacketReader:                        "bno08x packet reader cannot be nil",
		ErrorCodeBNO08XNilPacketWriter:                        "bno08x packet writer cannot be nil",
		ErrorCodeBNO08XNilUARTBus:                             "bno08x uart bus cannot be nil",
		ErrorCodeBNO08XFailedToConfigureUART:                  "bno08x failed to configure uart",
		ErrorCodeBNO08XFailedToResetUARTRVC:                   "bno08x failed to reset uart rvc",
		ErrorCodeBNO08XUARTRVCNilFrame:                        "bno08x uart rvc frame cannot be nil",
		ErrorCodeBNO08XUARTRVCFrameTooShort:                   "bno08x uart rvc frame too short",
		ErrorCodeBNO08XUARTRVCInvalidChecksum:                 "bno08x uart rvc invalid checksum",
		ErrorCodeBNO08XUARTRVCByteTimeout:                     "bno08x uart rvc byte timeout",
		ErrorCodeBNO08XUARTRVCFailedToReadByte:                "bno08x uart rvc failed to read byte",
		ErrorCodeBNO08XFailedToParseFrame:                     "bno08x failed to parse frame",
		ErrorCodeBNO08XUARTRVCUARTTimeout:                     "bno08x uart rvc uart timeout",
		ErrorCodeBNO08XFailedToCreatePacket:                   "bno08x failed to create packet",
		ErrorCodeBNO08XFailedToSetUARTFormat:                  "bno08x failed to set uart format",
		ErrorCodeBNO08XFailedToCreatePacketReader:             "bno08x failed to create packet reader",
		ErrorCodeBNO08XFailedToCreatePacketWriter:             "bno08x failed to create packet writer",
		ErrorCodeBNO08XUARTByteTimeout:                        "bno08x uart byte timeout",
		ErrorCodeBNO08XUARTFailedToReadByte:                   "bno08x uart failed to read byte",
		ErrorCodeBNO08XFailedToResetBNO08X:                    "bno08x failed to reset bno08x",
		ErrorCodeBNO08XNilPacketBuffer:                        "bno08x packet buffer cannot be nil",
		ErrorCodeBNO08XFailedToGetExpectedReportLength:        "bno08x failed to get expected report length",
		ErrorCodeBNO08XInvalidReportLength:                    "bno08x invalid report length",
		ErrorCodeBNO08XFailedToGetReportID:                    "bno08x failed to get report id",
		ErrorCodeBNO08XInsertCommandRequestReportBufferTooShort: "bno08x insert command request report buffer too short",
		ErrorCodeBNO08XInsertCommandRequestReportTooManyArguments: "bno08x insert command request report too many arguments",
		ErrorCodeBNO08XUnknownReportID:                        "bno08x unknown report id",
		ErrorCodeBNO08XFailedToCreatePacketFromBuffer:         "bno08x failed to create packet from buffer",
		ErrorCodeBNO08XFailedToCreateReportFromPacketBuffer:   "bno08x failed to create report from packet buffer",
		ErrorCodeBNO08XInvalidReportIDToParseReport:           "bno08x invalid report id to parse report",
		ErrorCodeBNO08XInvalidReportStabilityClassificationUint8: "bno08x invalid report stability classification uint8",
		ErrorCodeBNO08XInvalidReportActivityUint8:             "bno08x invalid report activity uint8",
		ErrorCodeBNO08XInvalidReportIDForFourDimensionalParsing: "bno08x invalid report id for four dimensional parsing",
		ErrorCodeBNO08XInvalidReportIDForThreeDimensionalParsing: "bno08x invalid report id for three dimensional parsing",
		ErrorCodeBNO08XInvalidReportAccuracyStatusUint8:       "bno08x invalid report accuracy status uint8",
		ErrorCodeBNO08XSensorReportDataTooShort:               "bno08x sensor report data too short",
		ErrorCodeBNO08XNoPacketAvailable:                      "bno08x no packet available",
		ErrorCodeBNO08XInvalidReportDataLength:               "bno08x invalid report data length",
		ErrorCodeBNO08XUARTEndMissing:                        "bno08x uart end missing",
		ErrorCodeBNO08XPacketHeaderBufferTooShort:            "bno08x packet header buffer too short",
		ErrorCodeBNO08XNilDestinationBuffer:                  "bno08x destination buffer cannot be nil",
		ErrorCodeBNO08XInvalidStartOrEndIndex:                "bno08x invalid start or end index",
		ErrorCodeBNO08XNilPacketData:                         "bno08x packet data cannot be nil",
		ErrorCodeBNO08XCommandRequestReportNilBuffer:         "bno08x command request report buffer cannot be nil",
		ErrorCodeBNO08XNilReportData:                         "bno08x report data cannot be nil",
		ErrorCodeBNO08XNilCommandRequestReportParameters:     "bno08x command request report parameters cannot be nil",
		ErrorCodeBNO08XPacketDataTooShort:                    "bno08x packet data too short",
		ErrorCodeBNO08XI2CFailedToProbeDevice:               "bno08x i2c failed to probe device",
		ErrorCodeBNO08XI2CFailedToProbeDeviceRepeatly:        "bno08x i2c failed to probe device repeatly",
		ErrorCodeBNO08XNilI2CBus:                            "bno08x i2c bus cannot be nil",
		ErrorCodeBNO08XInvalidI2CAddress:                    "bno08x invalid i2c address",
		ErrorCodeBNO08XFailedToConfigureI2C:                 "bno08x failed to configure i2c",
		ErrorCodeBNO08XI2CFailedToWritePacketHeaderBuffer:   "bno08x i2c failed to write packet header buffer",
		ErrorCodeBNO08XI2CFailedToWritePacketPacketBuffer:   "bno08x i2c failed to write packet packet buffer",
		ErrorCodeBNO08XPacketBufferTooShortForPacketHeader:  "bno08x packet buffer too short for packet header",
		ErrorCodeBNO08XPacketBufferTooShortForPacket:        "bno08x packet buffer too short for packet",
		ErrorCodeBNO08XI2CFailedToReadRequestedDataLength:   "bno08x i2c failed to read requested data length",
		ErrorCodeBNO08XInvalidPacketSize:                    "bno08x invalid packet size",
		ErrorCodeBNO08XNilSPIBus:                            "bno08x spi bus cannot be nil",
		ErrorCodeBNO08XFailedToConfigureSPI:                 "bno08x failed to configure spi",
		ErrorCodeBNO08XFailedToWakeUpSPI:                    "bno08x failed to wake up spi",
		ErrorCodeBNO08XSPIFailedToWritePacketHeaderBuffer:   "bno08x spi failed to write packet header buffer",
		ErrorCodeBNO08XSPIFailedToWritePacketPacketBuffer:   "bno08x spi failed to write packet packet buffer",
		ErrorCodeBNO08XSPIFailedToReadRequestedDataLength:   "bno08x spi failed to read requested data length",
		ErrorCodeBNO08XFailedToEnableDependencyFeature:      "bno08x failed to enable dependency feature",
		ErrorCodeBNO08XFailedToEnableFeature:                "bno08x failed to enable feature",
		ErrorCodeBNO08XFailedToBeginCalibration:             "bno08x failed to begin calibration",
		ErrorCodeBNO08XNilSubcommandParams:                  "bno08x subcommand params cannot be nil",
		ErrorCodeBNO08XFailedToInsertCommandRequestReport:   "bno08x failed to insert command request report",
		ErrorCodeBNO08XFailedToSendMeCommandRequestPacket:   "bno08x failed to send me command request packet",
		ErrorCodeBNO08XFailedToSendCommandRequestPacketToSaveCalibrationData: "bno08x failed to send command request packet to save calibration data",
		ErrorCodeBNO08XFailedToSaveCalibrationData:          "bno08x failed to save calibration data",
		ErrorCodeBNO08XFailedToSendResetCommandRequestPacket: "bno08x failed to send reset command request packet",
		ErrorCodeBNO08XFailedToReadSensorID:                 "bno08x failed to read sensor id",
		ErrorCodeBNO08XFailedToSendProductIDRequestPacket:   "bno08x failed to send product id request packet",
		ErrorCodeBNO08XWaitingForPacketTimedOut:             "bno08x waiting for packet timed out",
		ErrorCodeBNO08XMismatchedPacketDataLength:           "bno08x mismatched packet data length",
		ErrorCodeBNO08XFailedToSaveDynamicCalibrationData:   "bno08x failed to save dynamic calibration data",
		ErrorCodeBNO08XFailedToParseGetFeatureReport:        "bno08x failed to parse get feature report",
		ErrorCodeBNO08XFailedToParseSensorID:                "bno08x failed to parse sensor id",
		ErrorCodeBNO08XFailedToParseRawMagnetometerReport:   "bno08x failed to parse raw magnetometer report",
		ErrorCodeBNO08XFailedToParseStepCounterReport:       "bno08x failed to parse step counter report",
		ErrorCodeBNO08XFailedToParseShakeReport:             "bno08x failed to parse shake report",
		ErrorCodeBNO08XFailedToParseStabilityClassifierReport: "bno08x failed to parse stability classifier report",
		ErrorCodeBNO08XFailedToParseActivityClassifierReport: "bno08x failed to parse activity classifier report",
		ErrorCodeBNO08XFailedToParseMagnetometerReport:      "bno08x failed to parse magnetometer report",
		ErrorCodeBNO08XFailedToParseRotationVectorReport:    "bno08x failed to parse rotation vector report",
		ErrorCodeBNO08XFailedToParseGeomagneticRotationVectorReport: "bno08x failed to parse geomagnetic rotation vector report",
		ErrorCodeBNO08XFailedToParseGameRotationVectorReport: "bno08x failed to parse game rotation vector report",
		ErrorCodeBNO08XFailedToParseAccelerometerReport:   "bno08x failed to parse accelerometer report",
		ErrorCodeBNO08XFailedToParseLinearAccelerationReport: "bno08x failed to parse linear acceleration report",
		ErrorCodeBNO08XFailedToParseGravityReport:          "bno08x failed to parse gravity report",
		ErrorCodeBNO08XFailedToParseGyroscopeReport:        "bno08x failed to parse gyroscope report",
		ErrorCodeBNO08XFailedToParseRawGyroscopeReport:     "bno08x failed to parse raw gyroscope report",
		ErrorCodeBNO08XFailedToParseRawAccelerometerReport: "bno08x failed to parse raw accelerometer report",
		ErrorCodeBNO08XFailedToGetReportLengthForTheGivenReportID: "bno08x failed to get report length for the given report id",
		ErrorCodeBNO08XUnprocessableBatchBytes:            "bno08x unprocessable batch bytes",
		ErrorCodeBNO08XI2CFailedToReadPacketHeader:        "bno08x i2c failed to read packet header",
		ErrorCodeBNO08XSPIFailedToReadPacketHeader:        "bno08x spi failed to read packet header",
		ErrorCodeBNO08XUnhandledUARTControlSHTPProtocol:   "bno08x unhandled uart control shtp protocol",
		ErrorCodeBNO08XNilBNO08XInstance:                  "bno08x instance cannot be nil",
		ErrorCodeBNO08XSetFeatureEnableReportDataNilBuffer: "bno08x set feature enable report data buffer cannot be nil",
		ErrorCodeBNO08XSetFeatureEnableReportDataBufferTooShort: "bno08x set feature enable report data buffer too short",
		ErrorCodeBNO08XNilPacketHeaderBuffer:              "bno08x packet header buffer cannot be nil",
		ErrorCodeBNO08XReportHeaderBufferTooShort:         "bno08x report header buffer too short",
		ErrorCodeBNO08XNilWaitForPacketFunction:           "bno08x wait for packet function cannot be nil",
		ErrorCodeBNO08XInvalidMode:                        "bno08x invalid mode",
		ErrorCodeBNO08XUnknownModeAttemptingSoftwareReset: "bno08x unknown mode attempting software reset",
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
