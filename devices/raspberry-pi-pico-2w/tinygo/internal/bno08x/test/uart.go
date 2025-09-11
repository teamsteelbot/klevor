//go:build tinygo && (rp2040 || rp2350)

package tinygo_bno08x

import (
	"time"

	"machine"

	tinygotypes "github.com/ralvarezdev/tinygo-types"
)

type (
	// UART is the UART implementation of the BNO08X sensor
	UART struct {
		*BNO08X
		uartBus  *machine.UART
		ps0Pin   machine.Pin
		ps1Pin   machine.Pin
		resetPin machine.Pin
	}

	// UARTPacketReader is the packet reader for UART interface
	UARTPacketReader struct {
		uartBus    *machine.UART
		dataBuffer DataBuffer
		debugger   Debugger
		ultraDebug bool
	}

	// UARTPacketWriter is the packet writer for UART interface
	UARTPacketWriter struct {
		uartBus    *machine.UART
		dataBuffer DataBuffer
		debugger   Debugger
		ultraDebug bool
	}

	// UARTOptions struct for configuring the BNO08X over UART.
	UARTOptions struct {
		Options    *Options
		UltraDebug bool
	}
)

// NewUARTOptions creates a new UARTOptions instance with default values.
//
// Parameters:
//
// debugger: The debugger to use for logging and debugging information (optional).
// ultraDebug: Flag to enable ultra debug mode (optional).
//
// Returns:
//
// A pointer to a new UARTOptions instance.
func NewUARTOptions(
	debugger Debugger,
	ultraDebug bool,
) *UARTOptions {
	return &UARTOptions{
		Options:    NewOptions(debugger),
		UltraDebug: ultraDebug,
	}
}

// NewUART creates a new UART instance for the BNO08X sensor
//
// Parameters:
//
// uartBus: The UART bus to use for communication.
// txPin: The TX pin for UART communication.
// rxPin: The RX pin for UART communication.
// ps0Pin: The PS0 pin to set the sensor to UART mode.
// ps1Pin: The PS1 pin to set the sensor to UART mode.
// resetPin: The pin used to reset the BNO08X sensor.
// dataBuffer: The data buffer to use for storing Packet data.
//
//	afterResetFn: An optional function to be called after a reset.
//
// options: The UARTOptions for configuring the BNO08X (optional).
//
// Returns:
//
// A pointer to a new UART instance and an error if any occurs.
func NewUART(
	uartBus *machine.UART,
	txPin machine.Pin,
	rxPin machine.Pin,
	ps0Pin machine.Pin,
	ps1Pin machine.Pin,
	resetPin machine.Pin,
	dataBuffer DataBuffer,
	afterResetFn func(b *BNO08X) tinygotypes.ErrorCode,
	options *UARTOptions,
) (*UART, tinygotypes.ErrorCode) {
	// Check if the UART bus is nil
	if uartBus == nil {
		return nil, ErrorCodeBNO08XNilUARTBus
	}

	// Set PS0 pin to output and low
	ps0Pin.Configure(machine.PinConfig{Mode: machine.PinOutput})
	ps0Pin.Low()

	// Set PS1 pin to output and high
	ps1Pin.Configure(machine.PinConfig{Mode: machine.PinOutput})
	ps1Pin.High()

	// Configure UART
	if err := uartBus.Configure(
		machine.UARTConfig{
			BaudRate: UARTBaudRate,
			TX:       txPin,
			RX:       rxPin,
		},
	); err != nil {
		return nil, ErrorCodeBNO08XFailedToConfigureUART
	}

	// Set UART format (8N1)
	if err := uartBus.SetFormat(UARTDataBits, UARTStopBits, UARTParity); err != nil {
		return nil, ErrorCodeBNO08XFailedToSetUARTFormat
	}

	// If options are nil, initialize with default values
	if options == nil {
		options = NewUARTOptions(nil, false)
	}

	// Get the debugger from options
	debugger := options.Options.Debugger

	// Create packet reader and writer
	packetReader, err := newUARTPacketReader(
		uartBus,
		dataBuffer,
		debugger,
		options.UltraDebug,
	)
	if err != tinygotypes.ErrorCodeNil {
		return nil, ErrorCodeBNO08XFailedToCreatePacketReader
	}

	packetWriter, err := newUARTPacketWriter(
		uartBus,
		dataBuffer,
		debugger,
		options.UltraDebug,
	)
	if err != tinygotypes.ErrorCodeNil {
		return nil, ErrorCodeBNO08XFailedToCreatePacketWriter
	}

	// Initialize BNO08X
	bno08x, err := NewBNO08X(
		resetPin,
		packetReader,
		packetWriter,
		dataBuffer,
		nil,
		afterResetFn,
		options.Options,
	)
	if err != tinygotypes.ErrorCodeNil {
		return nil, ErrorCodeBNO08XFailedToCreateBNO08X
	}

	return &UART{
		BNO08X:   bno08x,
		uartBus:  uartBus,
		ps1Pin:   ps1Pin,
		ps0Pin:   ps0Pin,
		resetPin: resetPin,
	}, tinygotypes.ErrorCodeNil
}

// GetBNO08X returns the BNO08X instance.
//
// Returns:
//
// The BNO08X instance.
func (uart *UART) GetBNO08X() *BNO08X {
	return uart.BNO08X
}

// newUARTPacketReader creates a new UARTPacketReader instance.
//
// Parameters:
//
// uartBus: The UART bus to use for communication.
// debugger: The debugger to use for logging and debugging information.
// dataBuffer: The data buffer to use for storing Packet data.
// ultraDebug: Flag to enable ultra debug mode (optional).
//
// Returns:
//
// A pointer to a new UARTPacketReader instance.
func newUARTPacketReader(
	uartBus *machine.UART,
	dataBuffer DataBuffer,
	debugger Debugger,
	ultraDebug bool,
) (*UARTPacketReader, tinygotypes.ErrorCode) {
	// Check if the UART bus is nil
	if uartBus == nil {
		return nil, ErrorCodeBNO08XNilUARTBus
	}

	// Check if the dataBuffer is provided
	if dataBuffer == nil {
		return nil, ErrorCodeBNO08XNilDataBuffer
	}

	return &UARTPacketReader{
		uartBus:    uartBus,
		debugger:   debugger,
		dataBuffer: dataBuffer,
		ultraDebug: ultraDebug,
	}, tinygotypes.ErrorCodeNil
}

// IsDataReady checks if data is available on UART
//
// Returns:
//
// True if data is available, otherwise false.
func (pr *UARTPacketReader) IsDataReady() bool {
	return pr.uartBus.Buffered() >= PacketHeaderLength
}

// readByte blocks until a byte is read (simple poll).
//
// Returns:
//
// A byte read from UART and an error if any.
func (pr *UARTPacketReader) readByte() (byte, tinygotypes.ErrorCode) {
	startTime := time.Now()
	for time.Since(startTime) < UARTByteTimeout {
		if pr.uartBus.Buffered() > 0 {
			b, err := pr.uartBus.ReadByte()
			if err != nil {
				return b, ErrorCodeBNO08XUARTFailedToReadByte
			}
			if pr.debugger != nil && pr.ultraDebug {
				pr.debugger.Debug("Received byte")
			}
			return b, tinygotypes.ErrorCodeNil
		}
		time.Sleep(NoByteDelay)
	}
	return 0, ErrorCodeBNO08XUARTRVCByteTimeout
}

// readInto reads bytes into the destination buffer handling escape sequences.
//
// Parameters:
//
// dst: The destination byte slice to read into.
// start: The starting index in the destination slice.
// end: The ending index in the destination slice.
//
// Returns:
//
// An error if any occurs during reading.
func (pr *UARTPacketReader) readInto(dst []byte, start int, end int) tinygotypes.ErrorCode {
	// Check if the destination slice is nil
	if dst == nil {
		return ErrorCodeBNO08XNilDestinationBuffer
	}

	// Check if start and end are within bounds
	if start < 0 || end > len(dst) || start >= end {
		return ErrorCodeBNO08XInvalidStartOrEndIndex
	}

	// Read bytes into the destination slice
	for i := start; i < end; i++ {
		b, err := pr.readByte()
		if err != tinygotypes.ErrorCodeNil {
			return err
		}
		if b == UARTControlEscape {
			nb, err := pr.readByte()
			if err != tinygotypes.ErrorCodeNil {
				return err
			}
			b = nb ^ 0x20
		}
		dst[i] = b
	}
	return tinygotypes.ErrorCodeNil
}

// readHeader reads the UART packet header.
//
// Returns:
//
// An error if any occurs during reading.
func (pr *UARTPacketReader) readHeader() tinygotypes.ErrorCode {
	// Find first initial start byte
	for {
		b, err := pr.readByte()
		if err != tinygotypes.ErrorCodeNil {
			return err
		}
		if b == UARTStartAndEndByte {
			break
		}
	}

	// Read protocol ID sequence
	data, err := pr.readByte()
	if err != tinygotypes.ErrorCodeNil {
		return err
	}
	if data == UARTStartAndEndByte {
		// Consume next (real protocol byte)
		data, err = pr.readByte()
		if err != tinygotypes.ErrorCodeNil {
			return err
		}
	}
	if data != UARTSHTPByte {
		return ErrorCodeBNO08XUnhandledUARTControlSHTPProtocol
	}
	return pr.readInto(pr.dataBuffer.GetData(), 0, PacketHeaderLength)
}

// ReadPacket reads a packet from UART
//
// Returns:
//
// A Packet object and an error if any occurs.
func (pr *UARTPacketReader) ReadPacket() (*Packet, tinygotypes.ErrorCode) {
	// Read packet header
	if err := pr.readHeader(); err != tinygotypes.ErrorCodeNil {
		return nil, err
	}

	// Parse header
	header, err := NewPacketHeaderFromBuffer(pr.dataBuffer.GetData())
	if err != tinygotypes.ErrorCodeNil {
		return nil, err
	}
	if header.PacketByteCount == 0 {
		return nil, ErrorCodeBNO08XNoPacketAvailable
	}
	channelNumber := header.ChannelNumber

	// Check if the channel number is valid
	if channelNumber > MaxChannelNumber {
		return nil, ErrorCodeBNO08XInvalidChannelNumber
	}

	// Check the data length for the packet
	if header.DataLength > MaxDataLength {
		return nil, ErrorCodeBNO08XInvalidReportDataLength
	}

	// Debug log the header
	if pr.debugger != nil && pr.ultraDebug {
		pr.debugger.DebugBuffer(header.PrintBuffer(false))
	}

	// Read remaining (payload) bytes
	dataBuffer := pr.dataBuffer.GetData()
	if err = pr.readInto(
		dataBuffer,
		PacketHeaderLength,
		int(header.PacketByteCount),
	); err != tinygotypes.ErrorCodeNil {
		return nil, err
	}

	// Expect trailing 0x7E
	endByte, err := pr.readByte()
	if err != tinygotypes.ErrorCodeNil {
		return nil, err
	}
	if endByte != UARTStartAndEndByte {
		return nil, ErrorCodeBNO08XUARTEndMissing
	}

	// Construct packet data
	packetData := make([]byte, header.DataLength)
	copy(packetData, dataBuffer[PacketHeaderLength:header.PacketByteCount])

	// Initialize packet
	packet, err := NewPacket(packetData, header)
	if err != tinygotypes.ErrorCodeNil {
		return nil, err
	}

	// Debug log the packet
	if pr.debugger != nil {
		pr.debugger.DebugBuffer(packet.PrintBuffer(false))
	}

	// Update sequence number
	if err := pr.dataBuffer.UpdateSequenceNumber(packet); err != tinygotypes.ErrorCodeNil {
		return nil, err
	}
	return packet, tinygotypes.ErrorCodeNil
}

// newUARTPacketWriter creates a new UARTPacketWriter instance.
//
// Parameters:
//
// uartBus: The UART bus to use for communication.
// dataBuffer: The data buffer to use for storing Packet data.
// debugger: The debugger to use for logging and debugging information.
// ultraDebug: Flag to enable ultra debug mode (optional).
//
// Returns:
//
// A pointer to a new UARTPacketWriter instance, or an error if the dataBuffer is nil.
func newUARTPacketWriter(
	uartBus *machine.UART,
	dataBuffer DataBuffer,
	debugger Debugger,
	ultraDebug bool,
) (*UARTPacketWriter, tinygotypes.ErrorCode) {
	// Check if the UART bus is nil
	if uartBus == nil {
		return nil, ErrorCodeBNO08XNilUARTBus
	}

	// Check if the dataBuffer is provided
	if dataBuffer == nil {
		return nil, ErrorCodeBNO08XNilDataBuffer
	}

	return &UARTPacketWriter{
		uartBus:    uartBus,
		debugger:   debugger,
		dataBuffer: dataBuffer,
		ultraDebug: ultraDebug,
	}, tinygotypes.ErrorCodeNil
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
func (pw *UARTPacketWriter) SendPacket(channel uint8, data []byte) (
	uint8,
	tinygotypes.ErrorCode,
) {
	// Check if the data is nil
	if data == nil {
		return 0, ErrorCodeBNO08XNilPacketData
	}

	// Get channel sequence number
	sequenceNumber, err := pw.dataBuffer.GetSequenceNumber(channel)
	if err != tinygotypes.ErrorCodeNil {
		return 0, err
	}

	// Initialize the packet from data
	packet, err := NewPacketFromData(
		channel,
		sequenceNumber,
		data,
	)
	if err != tinygotypes.ErrorCodeNil {
		return 0, err
	}

	// Debug log the packet
	if pw.debugger != nil {
		pw.debugger.DebugBuffer(packet.Header.PrintBuffer(true))
		pw.debugger.DebugBuffer(packet.PrintBuffer(true))
	}

	// Send start byte
	pw.uartBus.WriteByte(UARTStartAndEndByte)
	time.Sleep(UARTByteDelay)

	// Send SHTP protocol byte
	pw.uartBus.WriteByte(UARTSHTPByte)
	time.Sleep(UARTByteDelay)

	// Send the packet header
	for _, b := range packet.Header.Buffer {
		pw.uartBus.WriteByte(b)
		time.Sleep(UARTByteDelay)
	}

	// Send the packet data
	for _, b := range packet.Data {
		pw.uartBus.WriteByte(b)
		time.Sleep(UARTByteDelay)
	}

	// Send start byte
	pw.uartBus.WriteByte(UARTStartAndEndByte)
	time.Sleep(UARTByteDelay)

	// Update sequence number
	sequenceNumber, err = pw.dataBuffer.IncrementChannelSequenceNumber(channel)
	if err != tinygotypes.ErrorCodeNil {
		return 0, err
	}
	return sequenceNumber, tinygotypes.ErrorCodeNil
}
