//go:build tinygo && (rp2040 || rp2350)

package tinygo_bno08x

import (
	"errors"

	tinygotypes "github.com/ralvarezdev/tinygo-types"
)

const (
	ErrInvalidReportIDForReportParsing = "invalid report id for report parsing, expected 0x%02X, got 0x%02X"
	ErrInvalidDataLength = 				"invalid data length in packet, exceeds maximum allowed length of %d bytes, got %d bytes"
	ErrMismatchedPacketDataLength = "mismatched packet data length, expected %d, got %d"
	ErrUnprocessableBatchBytes =  "unprocessable batch bytes for report id 0x%02X, required %d bytes, got %d bytes"
	ErrInvalidReportLength = 		"invalid report length for report id 0x%02X, expected %d bytes, got %d bytes"
)

var (
	ErrNilPacketBytes                            = errors.New("nil packet bytes provided for parsing")
	ErrNilReport                                 = errors.New("nil report provided for parsing")
	ErrNilReportData                             = errors.New("nil report data provided for parsing")
	ErrNilBuffer                                 = errors.New("nil buffer provided for reading data")
	ErrNilPacketReader                           = errors.New("packet reader is nil, cannot read data")
	ErrNilPacketWriter                           = errors.New("packet writer is nil, cannot write data")
	ErrNilDataBuffer                             = errors.New("nil data buffer provided for reading data")
	ErrReportDataTooShort                        = errors.New("report data are too short to parse")
	ErrStabilityClassifierTooShort               = errors.New("stability classifier report bytes are too short to parse")
	ErrBufferTooShort                            = errors.New("buffer is too short to read the expected data")
	ErrBufferTooShortForHeader                   = errors.New("buffer is too short to read the packet header")
	ErrPacketDataTooShort                        = errors.New("packet data is too short to read the expected data")
	ErrUnknownReportID                           = errors.New("unknown report id received from sensor")
	ErrNilSensorReport                           = errors.New("nil sensor report provided for parsing")
	ErrCommandRequestTooManyArguments            = errors.New("command request cannot have more than 9 arguments")
	ErrFailedToReadSensorID                      = errors.New("failed to read sensor id from the device")
	ErrPacketTimeout                             = errors.New("packet read timeout exceeded")
	ErrFailedToSaveCalibrationData               = errors.New("failed to save calibration data to the device")
	ErrInvalidReportIDForThreeDimensionalParsing = errors.New("invalid report id for three-dimensional parsing")
	ErrInvalidReportIDForFourDimensionalParsing  = errors.New("invalid report id for four-dimensional parsing")
	ErrNoPacketAvailable                         = errors.New("no packet available to read from the i2c bus")
	ErrNilI2CBus                                 = errors.New("nil i2c bus provided for communication")
	ErrInvalidI2CAddress                         = errors.New("invalid i2c address provided")
	ErrNilDestinationBuffer                      = errors.New("nil destination buffer provided for uart read")
	ErrUnhandledUARTControlSHTPProtocol          = errors.New("unhandled uart control shtp protocol")
	ErrUARTEndMissing                            = errors.New("uart end byte missing from packet")
	ErrNilPacketHeaderString                     = errors.New("nil packet header string provided for parsing")
	ErrNilPacketString                           = errors.New("nil packet string provided for parsing")
	ErrNilPacketData                             = errors.New("nil packet data provided for parsing")
	ErrNilPacketBuffer                           = errors.New("nil packet buffer provided for parsing")
	ErrNilPacketHeaderBuffer                     = errors.New("nil packet header buffer provided for parsing")
	ErrUARTTimeout                               = errors.New("uart read timeout exceeded")
	ErrNilSubcommandParams                       = errors.New("nil subcommand parameters provided")
	ErrInvalidMaxPackets                         = errors.New("invalid max packets value provided")
	ErrNilUARTBus                                = errors.New("nil uart bus provided for communication")
	ErrMaxCalibrationAttemptsExceeded            = errors.New("maximum calibration attempts exceeded")
	ErrRVCTimeout                                = errors.New("unable to read rvc heading message")
	ErrInvalidChecksum                           = errors.New("invalid checksum")
	ErrNilRotationVector                         = errors.New("nil rotation vector provided for parsing")
	ErrNilFrame                                  = errors.New("nil frame provided for parsing")
	ErrFrameTooShort                             = errors.New("frame data are too short to parse")
	ErrNilBNO08X                                 = errors.New("nil BNO08x instance provided")
	ErrNilBNO08XService                          = errors.New("nil BNO08x service provided")
	ErrNilEulerDegrees                           = errors.New("nil euler degrees provided")
	ErrSPICouldNotBeWokenUp                     = errors.New("spi could not be woken up from sleep mode")
)

const (
	// ErrorCodeBNO08XStartNumber is the starting number for BNO08X-related error codes.
	ErrorCodeBNO08XStartNumber uint16 = 5000
)

const (
	ErrorCodeBNO08XDataBufferIndexOutOfRange tinygotypes.ErrorCode = tinygotypes.ErrorCode(iota + ErrorCodeBNO08XStartNumber)
	ErrorCodeBNO08XInvalidChannelNumber
	ErrorCodeBNO08XNilPacket
	ErrorCodeBNO08XNilPacketHeader
	ErrorCodeBNO08XNilUARTBus
	ErrorCodeBNO08XFailedToConfigureUART
	ErrorCodeBNO08XFailedToInitializeUARTRVC
	ErrorCodeBNO08XNilRotationVector
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
	ErrorCodeBNO08XFailedToCreateBNO08X
	ErrorCodeBNO08XUARTByteTimeout
	ErrorCodeBNO08XUARTFailedToReadByte
	ErrorCodeBNO08XFailedToInitializeBNO08X
	ErrorCodeBNO08XNilDataBuffer
	ErrorCodeBNO08XFailedToGetExpectedReportLength
	ErrorCodeBNO08XInvalidReportLength
	ErrorCodeBNO08XNilReport
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
	ErrorCodeBNO08XNilSensorReport
	ErrorCodeBNO08XInvalidReportAccuracyStatusUint8
	ErrorCodeBNO08XSensorReportDataTooShort
	ErrorCodeBNO08XNoPacketAvailable
	ErrorCodeBNO08XNilPacketBuffer
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
	ErrorCodeBNO08XI2CFailedToWritePacketDataBuffer
	ErrorCodeBNO08XDataBufferTooShortForPacketHeader
	ErrorCodeBNO08XI2CFailedToReadRequestedDataLength
	ErrorCodeBNO08XInvalidPacketSize
	ErrorCodeBNO08XNilSPIBus
	ErrorCodeBNO08XFailedToConfigureSPI
	ErrorCodeBNO08XFailedToWakeUpSPI
	ErrorCodeBNO08XSPIFailedToWritePacketHeaderBuffer
	ErrorCodeBNO08XSPIFailedToWritePacketDataBuffer
	ErrorCodeBNO08XSPIFailedToReadRequestedDataLength
)