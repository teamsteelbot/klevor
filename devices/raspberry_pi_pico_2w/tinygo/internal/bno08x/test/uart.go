//go:build tinygo && (rp2040 || rp2350)

package test

import (
	"encoding/binary"
	"fmt"
	"time"

	"machine"
)

type (
	// UART represents the UART implementation of the BNO08X sensor
	UART struct {
		BNO08X
		uart *machine.UART
		ps1  machine.Pin
	}

	// UARTPacketReader represents the packet reader for UART interface
	UARTPacketReader struct {
		uart       *machine.UART
		dataBuffer DataBuffer
		debugger   Debugger
	}

	// UARTPacketWriter represents the packet writer for UART interface
	UARTPacketWriter struct {
		uart       *machine.UART
		dataBuffer DataBuffer
		debugger   Debugger
	}
)

// NewUART creates a new UART instance for the BNO08X sensor
func NewUART(
	uart *machine.UART,
	txPin machine.Pin,
	rxPin machine.Pin,
	ps1 machine.Pin,
	dataBuffer DataBuffer,
	options *Options,
) (*UART, error) {
	// Set PS1 pin to output and high
	ps1.Configure(machine.PinConfig{Mode: machine.PinOutput})
	ps1.High()

	// Configure UART
	err := uart.Configure(
		machine.UARTConfig{
			BaudRate: UARTBaudRate,
			TX:       txPin,
			RX:       rxPin,
		},
	)
	if err != nil {
		return nil, fmt.Errorf("failed to configure UART: %w", err)
	}

	// Get debugger from options
	var debugger Debugger
	if options != nil {
		debugger = options.Debugger
	}

	// Create packet reader and writer
	packetReader := &UARTPacketReader{
		uart:       uart,
		dataBuffer: dataBuffer,
		debugger:   debugger,
	}

	packetWriter := &UARTPacketWriter{
		uart:       uart,
		dataBuffer: dataBuffer,
		debugger:   debugger,
	}

	// Initialize BNO08X
	bno08x, err := NewBNO08X(
		packetReader,
		packetWriter,
		dataBuffer,
		true,
		options,
	)
	if err != nil {
		return nil, fmt.Errorf("failed to initialize BNO08X: %w", err)
	}

	return &UART{
		BNO08X: *bno08x,
		uart:   uart,
		ps1:    ps1,
	}, nil
}

// debug logs debug messages if debugger is enabled
//
// Parameters:
//
// args: The arguments to log.
func (r *UARTPacketReader) debug(args ...any) {
	if r.debugger != nil {
		r.debugger.Debug(args...)
	}
}

// IsDataReady checks if data is available on UART
//
// Returns:
//
// True if data is available, otherwise false.
func (r *UARTPacketReader) IsDataReady() bool {
	return r.uart.Buffered() >= PacketHeaderLength
}

// readByte blocks until a byte is read (simple poll).
//
// Returns:
//
// A byte read from UART and an error if any.
func (r *UARTPacketReader) readByte() (byte, error) {
	for {
		if r.uart.Buffered() > 0 {
			b, err := r.uart.ReadByte()
			return b, err
		}
		time.Sleep(200 * time.Microsecond)
	}
}

// readInto reads bytes into the destination buffer handling escape sequences.
//
// Parameters:
//
// dst: The destination byte slice to read into.
// start: The starting index in the destination slice.
// end: The ending index in the destination slice (optional).
//
// Returns:
//
// An error if any occurs during reading.
func (r *UARTPacketReader) readInto(dst *[]byte, start int, end *int) error {
	// Check if the dst is nil
	if dst == nil {
		return ErrNilDestinationBuffer
	}

	// Determine end index
	if end == nil {
		end = new(int)
		*end = len(*dst)
	}

	for i := start; i < *end; i++ {
		b, err := r.readByte()
		if err != nil {
			return err
		}
		if b == UARTControlEscape {
			nb, err := r.readByte()
			if err != nil {
				return err
			}
			b = nb ^ 0x20
		}
		(*dst)[i] = b
	}
	return nil
}

// readHeader reads the UART packet header.
//
// Returns:
//
// An error if any occurs during reading.
func (r *UARTPacketReader) readHeader() error {
	// Find first initial start byte
	for {
		b, err := r.readByte()
		if err != nil {
			return err
		}
		if b == UARTStartAndEndByte {
			break
		}
	}

	// Read protocol ID sequence
	data, err := r.readByte()
	if err != nil {
		return err
	}
	if data == UARTStartAndEndByte {
		// Consume next (real protocol byte)
		data, err = r.readByte()
		if err != nil {
			return err
		}
	}
	if data != UARTSHTPByte {
		return ErrUnhandledUARTControlSHTPProtocol
	}
	end := PacketHeaderLength
	return r.readInto(r.dataBuffer.GetData(), 0, &end)
}

// ReadPacket reads a packet from UART
//
// Returns:
//
// A Packet object and an error if any occurs.
func (r *UARTPacketReader) ReadPacket() (*Packet, error) {
	// Read packet header
	if err := r.readHeader(); err != nil {
		return nil, err
	}

	// Parse header
	header, err := NewPacketHeader(r.dataBuffer.GetData())
	if err != nil {
		return nil, err
	}
	if header.PacketByteCount == 0 {
		return nil, ErrNoPacketAvailable
	}

	// Debug
	channelNumber := header.ChannelNumber
	r.debug(
		fmt.Sprintf(
			"channel %d has %d bytes available",
			channelNumber,
			header.PacketByteCount-PacketHeaderLength,
		),
	)

	// Read remaining (payload) bytes
	end := int(header.PacketByteCount)
	dataBuffer := r.dataBuffer.GetData()
	if err = r.readInto(
		dataBuffer,
		PacketHeaderLength,
		&end,
	); err != nil {
		return nil, err
	}

	// Expect trailing 0x7E
	endByte, err := r.readByte()
	if err != nil {
		return nil, err
	}
	if endByte != UARTStartAndEndByte {
		return nil, ErrUARTEndMissing
	}

	// Construct packet data
	packetData := make([]byte, header.PacketByteCount)
	copy(packetData, (*dataBuffer)[:header.PacketByteCount])

	// Initialize packet
	packet := &Packet{
		Data:   packetData,
		Header: header,
	}

	// Update sequence number
	r.dataBuffer.UpdateSequenceNumber(packet)
	return packet, nil
}

// debug logs debug messages if debugger is enabled
//
// Parameters:
//
// args: The arguments to log.
func (w *UARTPacketWriter) debug(args ...any) {
	if w.debugger != nil {
		w.debugger.Debug(args...)
	}
}

// SendPacket sends a packet over UART
//
// Parameters:
//
// channel: The channel to send the packet on.
// data: The data to send in the packet.
//
// Returns:
//
// The sequence number used and an error if any occurs.
func (w *UARTPacketWriter) SendPacket(channel uint8, data []byte) (
	uint8,
	error,
) {
	// Build packet
	packetLength := len(data) + PacketHeaderLength
	packet := make([]byte, packetLength)

	// Header
	binary.LittleEndian.PutUint16(packet[0:2], uint16(packetLength))
	packet[2] = channel

	// Get sequence number
	seqNum, err := w.dataBuffer.GetSequenceNumber(channel)
	if err != nil {
		return 0, fmt.Errorf("failed to get sequence number: %w", err)
	}
	packet[3] = seqNum

	// Data
	copy(packet[PacketHeaderLength:], data)

	// Send start byte
	w.uart.WriteByte(UARTStartAndEndByte)
	time.Sleep(1 * time.Millisecond)

	// Send SHTP protocol byte
	w.uart.WriteByte(UARTSHTPByte)
	time.Sleep(1 * time.Millisecond)

	// Send packet with escape sequences
	for _, b := range packet {
		w.uart.WriteByte(b)
		time.Sleep(1 * time.Millisecond)
	}

	// Send start byte
	w.uart.WriteByte(UARTStartAndEndByte)
	time.Sleep(1 * time.Millisecond)

	// Update sequence number
	w.dataBuffer.IncrementChannelSequenceNumber(channel)

	w.debug(
		fmt.Sprintf(
			"Sent packet on channel %d len: %d",
			channel,
			packetLength,
		),
	)

	return seqNum, nil
}
