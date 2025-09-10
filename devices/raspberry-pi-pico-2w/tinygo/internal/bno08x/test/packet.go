//go:build tinygo && (rp2040 || rp2350)

package tinygo_bno08x

import (
	"encoding/binary"
	"strconv"
	"strings"

	tinygotypes "github.com/ralvarezdev/tinygo-types"
)

type (
	// PacketHeader represents the header of a BNO08x Packet
	PacketHeader struct {
		ChannelNumber   uint8
		SequenceNumber  uint8
		DataLength      int
		PacketByteCount int
		Buffer          [PacketHeaderLength]byte
	}

	// Packet represents a BNO08x Packet
	Packet struct {
		Header *PacketHeader
		Data   []byte
	}
)

// ChannelNumberString returns the string representation of the channel number.
//
// Returns:
//
// The channel number as a string.
func (h *PacketHeader) ChannelNumberString() string {
	switch ph.ChannelNumber {
	case ChannelSHTPCommand:
		return "SHTP_COMMAND"
	case ChannelExe:
		return "EXE"
	case ChannelControl:
		return "CONTROL"
	case ChannelInputSensorReports:
		return "INPUT_SENSOR_REPORTS"
	case ChannelWakeInputSensorReports:
		return "WAKE_INPUT_SENSOR_REPORTS"
	case ChannelGyroRotationVector:
		return "GYRO_ROTATION_VECTOR"
	default:
		return "UNKNOWN_CHANNEL"
	}
}

// SHTPCommandNameString returns the string representation of the SHTP command.
//
// Parameters:
//
// commandID: The command ID to get the name for.
//
// Returns:
//
// The command name as a string or "UNKNOWN_COMMAND" if not found.
func SHTPCommandNameString(commandID uint8) string {
	switch commandID {
	case ReportIDAccelerometer:
		return "ACCELEROMETER"
	case 0x29:
		return "ARVR_STABILIZED_GAME_ROTATION_VECTOR"
	case 0x28:
		return "ARVR_STABILIZED_ROTATION_VECTOR"
	case 0x22:
		return "CIRCLE_DETECTOR"
	case 0x1A:
		return "FLIP_DETECTOR"
	case ReportIDGameRotationVector:
		return "GAME_ROTATION_VECTOR"
	case ReportIDGeomagneticRotationVector:
		return "GEOMAGNETIC_ROTATION_VECTOR"
	case ReportIDGravity:
		return "GRAVITY"
	case ReportIDGyroscope:
		return "GYROSCOPE"
	case ReportIDLinearAcceleration:
		return "LINEAR_ACCELERATION"
	case ReportIDMagnetometer:
		return "MAGNETIC_FIELD"
	case ReportIDActivityClassifier:
		return "PERSONAL_ACTIVITY_CLASSIFIER"
	case 0x1B:
		return "PICKUP_DETECTOR"
	case 0x21:
		return "POCKET_DETECTOR"
	case ReportIDRawAccelerometer:
		return "RAW_ACCELEROMETER"
	case ReportIDRawGyroscope:
		return "RAW_GYROSCOPE"
	case ReportIDRawMagnetometer:
		return "RAW_MAGNETOMETER"
	case ReportIDRotationVector:
		return "ROTATION_VECTOR"
	case 0x17:
		return "SAR"
	case ReportIDShakeDetector:
		return "SHAKE_DETECTOR"
	case 0x12:
		return "SIGNIFICANT_MOTION"
	case 0x1F:
		return "SLEEP_DETECTOR"
	case ReportIDStabilityClassifier:
		return "STABILITY_CLASSIFIER"
	case 0x1C:
		return "STABILITY_DETECTOR"
	case ReportIDStepCounter:
		return "STEP_COUNTER"
	case 0x18:
		return "STEP_DETECTOR"
	case 0x10:
		return "TAP_DETECTOR"
	case 0x20:
		return "TILT_DETECTOR"
	case 0x07:
		return "UNCALIBRATED_GYROSCOPE"
	case 0x0F:
		return "UNCALIBRATED_MAGNETIC_FIELD"
	default:
		return "UNKNOWN_COMMAND"
	}
}

// ControlCommandNameString returns the string representation of the CONTROL command.
//
// Parameters:
//
// commandID: The command ID to get the name for.
//
// Returns:
//
// The command name as a string or "UNKNOWN_COMMAND" if not found.
func ControlCommandNameString(commandID uint8) string {
	switch commandID {
	case ReportIDError:
		return "ERROR"
	case ReportIDCoreConfiguration:
		return "CORE_CONFIGURATION"
	case ReportIDCoreConfigurationResponse:
		return "CORE_CONFIGURATION_RESPONSE"
	case ReportIDCommandRequest:
		return "COMMAND_REQUEST"
	case ReportIDCommandResponse:
		return "COMMAND_RESPONSE"
	case ReportIDFRSReadRequest:
		return "FRS_READ_REQUEST"
	case ReportIDFRSReadResponse:
		return "FRS_READ_RESPONSE"
	case ReportIDFRSWriteData:
		return "FRS_WRITE_DATA"
	case ReportIDFRSWriteRequest:
		return "FRS_WRITE_REQUEST"
	case ReportIDFRSWriteResponse:
		return "FRS_WRITE_RESPONSE"
	case ReportIDGetFeatureRequest:
		return "GET_FEATURE_REQUEST"
	case ReportIDGetFeatureResponse:
		return "GET_FEATURE_RESPONSE"
	case ReportIDSetFeatureCommand:
		return "SET_FEATURE_COMMAND"
	case ReportIDTimestampRebase:
		return "TIMESTAMP_REBASE"
	case ReportIDProductIDRequest:
		return "PRODUCT_ID_REQUEST"
	case ReportIDProductIDResponse:
		return "PRODUCT_ID_RESPONSE"
	default:
		return "UNKNOWN_COMMAND"
	}
}

// IsControlReportID checks if the report ID is a control report.
//
// Parameters:
//
//	reportID: The ID of the report
//
// Returns:
//
//	true if the report ID is a control report, false otherwise
func IsControlReportID(reportID uint8) bool {
	switch reportID {
	case ReportIDBaseTimestamp,
		ReportIDCommandRequest,
		ReportIDCommandResponse,
		ReportIDFRSReadRequest,
		ReportIDFRSReadResponse,
		ReportIDFRSWriteData,
		ReportIDFRSWriteRequest,
		ReportIDFRSWriteResponse,
		ReportIDGetFeatureRequest,
		ReportIDGetFeatureResponse,
		ReportIDSetFeatureCommand,
		ReportIDTimestampRebase,
		ReportIDProductIDRequest,
		ReportIDProductIDResponse:
		return true
	default:
		return false
	}
}

// ExeCommandNameString returns the string representation of the EXE command.
//
// Parameters:
//
// commandID: The command ID to get the name for.
//
// Returns:
//
// The command name as a string or "UNKNOWN_COMMAND" if not found.
func ExeCommandNameString(commandID uint8) string {
	switch commandID {
	case CommandReset:
		return "RESET"
	default:
		return "UNKNOWN_COMMAND"
	}
}

// NewPacketHeader creates a PacketHeader.
//
// Parameters:
//
// packetByteCount: The total byte count of the Packet.
// channelNumber: The channel number of the Packet.
// sequenceNumber: The sequence number of the Packet.
//
// Returns:
//
// A PacketHeader object.
func NewPacketHeader(
	packetByteCount uint16,
	channelNumber uint8,
	sequenceNumber uint8,
) *PacketHeader {
	dataLength := int(packetByteCount) - PacketHeaderLength
	if dataLength < 0 {
		dataLength = 0
	}

	// Initialize header buffer
	buffer := make([]byte, PacketHeaderLength)

	// First two bytes are writeLength (little-endian)
	buffer[0] = uint8(packetByteCount & 0xFF)
	buffer[1] = uint8((packetByteCount >> 8) & 0x7F)
	buffer[2] = channelNumber
	buffer[3] = sequenceNumber

	return &PacketHeader{
		ChannelNumber:   channelNumber,
		SequenceNumber:  sequenceNumber,
		DataLength:      dataLength,
		PacketByteCount: int(packetByteCount),
		Buffer:          buffer,
	}
}

// NewPacketHeaderFromBuffer creates a PacketHeader from a given buffer.
//
// Parameters:
//
//	buffer: A byte slice containing the Packet data.
//
// Returns:
//
//	A PacketHeader object or an error if the buffer is too short.
func NewPacketHeaderFromBuffer(buffer []byte) (*PacketHeader, tinygotypes.ErrorCode) {
	// Ensure the buffer is at least PacketHeaderLength bytes long to read the header
	if len(buffer) < PacketHeaderLength {
		return nil, ErrorCodeBNO08XPacketHeaderBufferTooShort
	}

	// Parse the header fields from the buffer
	packetByteCount := binary.LittleEndian.Uint16(buffer[0:2])
	packetByteCount &= 0x7FFF
	channelNumber := buffer[2]
	sequenceNumber := buffer[3]

	return &PacketHeader{
		ChannelNumber:   channelNumber,
		SequenceNumber:  sequenceNumber,
		DataLength:      int(packetByteCount) - PacketHeaderLength,
		PacketByteCount: int(packetByteCount),
		Buffer:          buffer,
	}, tinygotypes.ErrorCodeNil
}

// NewPacketHeaderFromData creates a PacketHeader from the provided data.
//
// Parameters:
//
// channelNumber: The channel number of the Packet.
// sequenceNumber: The sequence number of the Packet.
// data: A byte slice containing the Packet data.
//
// Returns:
//
// A PacketHeader object or an error if the data is nil.
func NewPacketHeaderFromData(
	channelNumber uint8,
	sequenceNumber uint8,
	data []byte,
) (*PacketHeader, tinygotypes.ErrorCode) {
	// Check if data is nil
	if data == nil {
		return nil, ErrorCodeBNO08XNilReportData
	}

	// Calculate packet byte count
	packetByteCount := len(data) + PacketHeaderLength

	return NewPacketHeader(
		uint16(packetByteCount),
		channelNumber,
		sequenceNumber,
	), tinygotypes.ErrorCodeNil
}

// IsError checks if the provided PacketHeader indicates an error condition.
//
// Parameters:
//
//	header: The PacketHeader to check.
//
// Returns:
//
//	True if the header indicates an error, otherwise false.
func (h *PacketHeader) IsError() bool {
	// Check if the channel number is greater than 5
	if h.ChannelNumber > 5 {
		return true
	}
	// Check if the Packet byte count and sequence number indicate an error
	if h.PacketByteCount == 0xFFFF && h.SequenceNumber == 0xFF {
		return true
	}
	return false
}

// PrintBuffer returns a byte slice representation of the PacketHeader for debugging purposes.
//
// Parameters:
//
// isBeingSent: A boolean indicating if the PacketHeader is being sent (true) or received (false).
//
// Returns:
//
// A byte slice containing the PacketHeader details.
func (ph *PacketHeader) PrintBuffer(isBeingSent bool) []byte {
	buffer := make([]byte, 0, 128) // Pre-allocate enough space

	if isBeingSent {
		buffer = append(buffer, "* SENDING PACKET HEADER *"...)
	} else {
		buffer = append(buffer, "* RECEIVED PACKET HEADER *"...)
	}

	buffer = append(buffer, "\n\t Data Length: "...)
	buffer = append(buffer, strconv.Itoa(ph.DataLength)...)

	buffer = append(buffer, "\n\t Channel: "...)
	buffer = append(buffer, ph.ChannelNumberString()...)

	buffer = append(buffer, "\n\t Sequence number: "...)
	buffer = append(buffer, strconv.Itoa(int(ph.SequenceNumber))...)
	return buffer
}

// NewPacket creates a new Packet from the provided data and header.
//
// Parameters:
//
//	data: A pointer to a byte slice containing the Packet data.
//	header: A pointer to the PacketHeader.
//
// Returns:
//
// A Packet object or an error if the data or header is nil.
func NewPacket(data []byte, header *PacketHeader) (*Packet, tinygotypes.ErrorCode) {
	// Check if data is nil
	if data == nil {
		return nil, ErrorCodeBNO08XNilReportData
	}

	// Check if the provided header is nil
	if header == nil {
		return nil, ErrorCodeBNO08XNilPacketHeader
	}

	return &Packet{
		Header: header,
		Data:   data,
	}, tinygotypes.ErrorCodeNil
}

// NewPacketFromBuffer creates a new Packet from the provided buffer.
//
// Parameters:
//
//	buffer: A pointer to a byte slice containing the Packet data.
//
// Returns:
//
//	A Packet object or an error if the Packet header could not be created.
func NewPacketFromBuffer(buffer []byte) (*Packet, tinygotypes.ErrorCode) {
	// Check if the provided buffer is nil
	if buffer == nil {
		return nil, ErrorCodeBNO08XNilPacketBuffer
	}

	// Create a new PacketHeader from the Packet bytes
	header, err := NewPacketHeaderFromBuffer(buffer)
	if err != nil {
		return nil, err
	}

	return &Packet{
		Header: header,
		Data:   buffer[PacketHeaderLength : PacketHeaderLength+header.DataLength],
	}, nil
}

// NewPacketFromData creates a new Packet from the provided data.
//
// Parameters:
//
// channelNumber: The channel number of the Packet.
// sequenceNumber: The sequence number of the Packet.
// data: A pointer to a byte slice containing the Packet data.
//
// Returns:
//
// A Packet object or an error if the data is nil.
func NewPacketFromData(
	channelNumber uint8,
	sequenceNumber uint8,
	data []byte,
) (*Packet, error) {
	// Check if data is nil
	if data == nil {
		return nil, ErrorCodeBNO08XNilReportData
	}

	// Create PacketHeader from data
	header, err := NewPacketHeaderFromData(
		channelNumber,
		sequenceNumber,
		data,
	)
	if err != nil {
		return nil, err
	}

	return &Packet{
		Header: header,
		Data:   data,
	}, nil
}

// SequenceNumber returns the sequence number of the Packet.
//
// Returns:
//
//	The sequence number as an uint8.
func (p *Packet) SequenceNumber() uint8 {
	return p.Header.SequenceNumber
}

// ReportID returns the report ID of the Packet.
//
// Returns:
//
//	The report ID as an uint8 or an error if the data is too short.
func (p *Packet) ReportID() (uint8, error) {
	if len(p.Data) < 1 {
		return 0, ErrorCodeBNO08XPacketDataTooShort
	}
	return p.Data[0], nil
}

// ChannelNumber returns the channel number of the Packet.
//
// Returns:
//
//	The channel number as an uint8.
func (p *Packet) ChannelNumber() uint8 {
	return p.Header.ChannelNumber
}

// PacketByteCount returns the total byte count of the Packet.
//
// Returns:
//
// The total byte count as an int.
func (p *Packet) PacketByteCount() int {
	return p.Header.PacketByteCount
}

// DataLength returns the data length of the Packet.
//
// Returns:
//
// The data length as an int.
func (p *Packet) DataLength() int {
	return p.Header.DataLength
}

// IsError checks if the Packet indicates an error condition.
//
// Returns:
//
//	True if the Packet is an error, otherwise false.
func (p *Packet) IsError() bool {
	return p.Header.IsError()
}

// PrintBuffer returns a byte slice representation of the Packet for debugging purposes.
//
// Parameters:
//
// isBeingSent: A boolean indicating if the Packet is being sent (true) or received (false).
//
// Returns:
//
// A byte slice containing the Packet details or nil if the Packet or its header is nil.
func (p *Packet) PrintBuffer(isBeingSent bool) []byte {
	if p.Header == nil {
		return nil
	}

	// Derive safe data length
	dataLen := p.Header.DataLength
	if dataLen > len(p.Data) {
		dataLen = len(p.Data)
	} else if dataLen < 0 {
		dataLen = 0
	}

	// Avoid multiple allocations by pre-allocating a sufficiently large buffer
	buffer := make([]byte, 0, 128)

	// Title
	if isBeingSent {
		buffer = append(buffer, "* SENDING PACKET *"...)
	} else {
		buffer = append(buffer, "* RECEIVED PACKET *"...)
	}

	// Data section
	buffer = append(buffer, "\n\t DATA"...)

	// Optional report decoding (guard length)
	var reportID uint8
	if dataLen == 0 {
		buffer = append(buffer, "\n\t\t Report Type: N/A"...)
		return buffer
	}

	reportID = p.Data[0]

	// Get the report type
	channelNumber := p.ChannelNumber()
	switch channelNumber {
	case ChannelSHTPCommand:
		reportIDStr = SHTPCommandNameString(reportID)
	case ChannelExe:
		reportIDStr = ExeCommandNameString(reportID)
	case ChannelControl:
		reportIDStr = ControlCommandNameString(reportID)
	case ChannelInputSensorReports:
		reportIDStr = ControlCommandNameString(reportID)
	}

	buffer = append(buffer, "\n\t\t Report Type: "...)
	buffer = append(buffer, reportIDStr...)
	buffer = append(buffer, " (0x"...)
	buffer = append(buffer, strings.ToUpper(strconv.FormatUint(uint64(reportID), 16))...)
	buffer = append(buffer, ")"...)

	// Additional interpretation (requires at least 6 data bytes)
	if dataLen < 6 {
		return buffer
	}

	// High report IDs (command responses / meta)
	if IsControlReportID(reportID) {
		sensorReportType := p.Data[5]
		buffer = append(buffer, "\n\t\t Sensor Report Type: "...)
		buffer = append(buffer, SHTPCommandNameString(sensorReportType)...)
		buffer = append(buffer, " (0x"...)
		buffer = append(buffer, strings.ToUpper(strconv.FormatUint(uint64(sensorReportType), 16))...)
		buffer = append(buffer, ")"...)
	}

	if reportID == ReportIDGetFeatureResponse || reportID == ReportIDSetFeatureCommand {
		featureID := p.Data[1]
		buffer = append(buffer, "\n\t\t Feature ID: "...)
		buffer = append(buffer, "0x"...)
		buffer = append(buffer, strings.ToUpper(strconv.FormatUint(uint64(featureID), 16))...)
		buffer = append(buffer, ")"...)
	}

	return buffer
}
