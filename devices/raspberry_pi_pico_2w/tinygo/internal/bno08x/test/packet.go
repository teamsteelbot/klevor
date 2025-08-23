//go:build tinygo && (rp2040 || rp2350)

package test

import (
	"encoding/binary"
	"fmt"
	"strings"
)

type (
	// PacketHeader represents the header of a BNO08x Packet
	PacketHeader struct {
		ChannelNumber   uint8
		SequenceNumber  uint8
		DataLength      int
		PacketByteCount int
	}

	// Packet represents a BNO08x Packet
	Packet struct {
		Header *PacketHeader
		Data   []byte
	}
)

// NewPacketHeader creates a PacketHeader from a given buffer.
//
// Parameters:
//
//	packetBytes: A pointer to a byte slice containing the Packet data.
//
// Returns:
//
//	A PacketHeader object or an error if the buffer is too short.
func NewPacketHeader(packetBytes *[]byte) (*PacketHeader, error) {
	// Check if the provided packetBytes is nil
	if packetBytes == nil {
		return nil, ErrNilPacketBytes
	}

	// Ensure the buffer is at least 4 bytes long to read the header
	if len(*packetBytes) < 4 {
		return nil, ErrBufferTooShortForHeader
	}

	packetByteCount := binary.LittleEndian.Uint16((*packetBytes)[0:2])
	packetByteCount &= ^uint16(0x8000)
	channelNumber := (*packetBytes)[2]
	sequenceNumber := (*packetBytes)[3]
	dataLength := int(packetByteCount) - 4
	if dataLength < 0 {
		dataLength = 0
	}

	return &PacketHeader{
		ChannelNumber:   channelNumber,
		SequenceNumber:  sequenceNumber,
		DataLength:      dataLength,
		PacketByteCount: int(packetByteCount),
	}, nil
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
func (header *PacketHeader) IsError() bool {
	// Check if the channel number is greater than 5
	if header.ChannelNumber > 5 {
		return true
	}
	// Check if the Packet byte count and sequence number indicate an error
	if header.PacketByteCount == 0xFFFF && header.SequenceNumber == 0xFF {
		return true
	}
	return false
}

// String returns a string representation of the PacketHeader for debugging purposes.
//
// Parameters:
//
// isBeingSent: A boolean indicating if the PacketHeader is being sent (true) or received (false).
//
// Returns:
//
// A string containing the PacketHeader details.
func (ph *PacketHeader) String(isBeingSent bool) *string {
	if ph == nil {
		return nil
	}
	var builder strings.Builder
	if isBeingSent {
		builder.WriteString("********** SENDING PACKET HEADER *************")
	} else {
		builder.WriteString("********** RECEIVED PACKET HEADER *************")
	}
	builder.WriteString(fmt.Sprintf("\n\t Data Length: %d", ph.DataLength))
	if int(ph.ChannelNumber) < len(Channels) {
		builder.WriteString(
			fmt.Sprintf(
				"\n\t Channel: %s (%d)",
				Channels[ph.ChannelNumber],
				ph.ChannelNumber,
			),
		)
	} else {
		builder.WriteString(
			fmt.Sprintf(
				"\n\t Channel: UNKNOWN (%d)",
				ph.ChannelNumber,
			),
		)
	}
	builder.WriteString(
		fmt.Sprintf(
			"\n\t Sequence number: %d",
			ph.SequenceNumber,
		),
	)
	builder.WriteString("\n\t *******************************")
	str := builder.String()
	return &str
}

// NewPacket creates a new Packet from the provided Packet bytes.
//
// Parameters:
//
//	packetBytes: A pointer to a byte slice containing the Packet data.
//
// Returns:
//
//	A Packet object or an error if the Packet header could not be created.
func NewPacket(packetBytes *[]byte) (*Packet, error) {
	// Check if the provided packetBytes is nil
	if packetBytes == nil {
		return nil, ErrNilPacketBytes
	}

	// Create a new PacketHeader from the Packet bytes
	header, err := NewPacketHeader(packetBytes)
	if err != nil {
		return nil, err
	}

	return &Packet{
		Header: header,
		Data:   (*packetBytes)[PacketHeaderLength : PacketHeaderLength+header.DataLength],
	}, nil
}

// ReportID returns the report ID of the Packet.
//
// Returns:
//
//	The report ID as an uint8 or an error if the data is too short.
func (p *Packet) ReportID() (uint8, error) {
	if len(p.Data) < 1 {
		return 0, ErrPacketDataTooShort
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

// IsError checks if the Packet indicates an error condition.
//
// Returns:
//
//	True if the Packet is an error, otherwise false.
func (p *Packet) IsError() bool {
	return p.Header.IsError()
}

// String returns a string representation of the Packet for debugging purposes.
//
// Parameters:
//
// isBeingSent: A boolean indicating if the Packet is being sent (true) or received (false).
//
// Returns:
//
//	A string containing the Packet details.
func (p *Packet) String(isBeingSent bool) *string {
	if p == nil || p.Header == nil {
		return nil
	}

	// Derive safe data length
	dataLen := p.Header.DataLength
	if dataLen > len(p.Data) {
		dataLen = len(p.Data)
	} else if dataLen < 0 {
		dataLen = 0
	}

	var builder strings.Builder
	if isBeingSent {
		builder.WriteString("********** SENDING PACKET *************")
	} else {
		builder.WriteString("********** RECEIVED PACKET *************")
	}
	builder.WriteString("\n\t HEADER")
	builder.WriteString(fmt.Sprintf("\n\t\t Data Length: %d", dataLen))

	if int(p.Header.ChannelNumber) < len(Channels) {
		builder.WriteString(
			fmt.Sprintf(
				"\n\t\t Channel: %s (%d)",
				Channels[p.Header.ChannelNumber],
				p.Header.ChannelNumber,
			),
		)
	} else {
		builder.WriteString(
			fmt.Sprintf(
				"\n\t\t Channel: UNKNOWN (%d)",
				p.Header.ChannelNumber,
			),
		)
	}

	builder.WriteString(
		fmt.Sprintf(
			"\n\t\t Sequence number: %d",
			p.Header.SequenceNumber,
		),
	)
	builder.WriteString("\n\n\t DATA")

	// Optional report decoding (guard length)
	if dataLen >= 1 {
		reportID := p.Data[0]
		if name, ok := Reports[reportID]; ok {
			builder.WriteString(
				fmt.Sprintf(
					"\n\t\t Report Type: %s (0x%02X)",
					name,
					reportID,
				),
			)
		} else {
			builder.WriteString(
				fmt.Sprintf(
					"\n\t\t Report Type: UNKNOWN (0x%02X)",
					reportID,
				),
			)
		}

		// Additional interpretation (requires at least 6 data bytes)
		if dataLen >= 6 {
			// High report IDs (command responses / meta)
			if reportID > 0xF0 {
				sensorReportType := p.Data[5]
				if name, ok := Reports[sensorReportType]; ok {
					builder.WriteString(
						fmt.Sprintf(
							"\n\t\t Sensor Report Type: %s (0x%02X)",
							name,
							sensorReportType,
						),
					)
				}
			}

			// 0xFC often used for "Get Feature Response" style packets
			if reportID == 0xFC {
				featureID := p.Data[1]
				if name, ok := Reports[featureID]; ok {
					builder.WriteString(
						fmt.Sprintf(
							"\n\t\t Enabled Feature: %s (0x%02X)",
							name,
							featureID,
						),
					)
				}
			}
		}
	}

	// Iterate only over actual data (exclude header bytes already removed)
	builder.WriteString("\n\t\t Bytes:")
	for idx := 0; idx < dataLen; idx++ {
		packetIdx := idx + 4 // original packet offset including header
		if (packetIdx % 4) == 0 {
			builder.WriteString(fmt.Sprintf("\n\t\t\t [0x%02X] ", packetIdx))
		}
		builder.WriteString(fmt.Sprintf("0x%02X ", p.Data[idx]))
	}

	builder.WriteString("\n\t *******************************")
	str := builder.String()
	return &str
}
