//go:build tinygo && (rp2040 || rp2350)

package tinygo_bno08x

import (
	"strconv"
	"time"

	"machine"

	tinygotypes "github.com/ralvarezdev/tinygo-types"
)

type (
	// SPI is the SPI implementation of the BNO08X sensor
	SPI struct {
		*BNO08X
		spiBus   *machine.SPI
		ps0Pin   machine.Pin
		ps1Pin   machine.Pin
		resetPin machine.Pin
		csPin    machine.Pin
		intPin   machine.Pin
	}

	// SPIPacketReader is the packet reader for SPI interface
	SPIPacketReader struct {
		spiBus     *machine.SPI
		intPin    machine.Pin
		dataBuffer DataBuffer
		debugger   Debugger
		ultraDebug bool
	}

	// SPIPacketWriter is the packet writer for SPI interface
	SPIPacketWriter struct {
		spiBus     *machine.SPI
		dataBuffer DataBuffer
		debugger   Debugger
		ultraDebug bool
	}

	// SPIOptions struct for configuring the BNO08X over SPI.
	SPIOptions struct {
		Options    *Options
		UltraDebug bool
	}
)

// NewSPIOptions creates a new SPIOptions instance with default values.
//
// Parameters:
//
// debugger: The debugger to use for logging and debugging information (optional).
// ultraDebug: Flag to enable ultra debug mode (optional).
//
// Returns:
//
// A pointer to a new SPIOptions instance.
func NewSPIOptions(
	debugger Debugger,
	ultraDebug bool,
) *SPIOptions {
	return &SPIOptions{
		Options:    NewOptions(debugger),
		UltraDebug: ultraDebug,
	}
}

// NewSPI creates a new SPI instance for the BNO08X sensor
//
// Parameters:
//
// spiBus: The SPI bus to use for communication.
// sckPin: The SCK pin for SPI communication.
// mosiPin: The MOSI pin for SPI communication.
// misoPin: The MISO pin for SPI communication.
// csPin: The CS pin for SPI communication.
// intPin: The INT pin for SPI communication.
// ps0Pin: The PS0 pin to set the sensor to SPI mode.
// ps1Pin: The PS1 pin to set the sensor to SPI mode.
// resetPin: The pin used to reset the BNO08X sensor.
// dataBuffer: The data buffer to use for storing Packet data.
// afterSoftwareResetFn: An optional function to be called after a reset.
// options: The SPIOptions for configuring the BNO08X (optional).
//
// Returns:
//
// A pointer to a new SPI instance and an error if any occurs.
func NewSPI(
	spiBus *machine.SPI,
	sckPin machine.Pin,
	mosiPin machine.Pin,
	misoPin machine.Pin,
	csPin machine.Pin,
	intPin machine.Pin,
	ps0Pin machine.Pin,
	ps1Pin machine.Pin,
	resetPin machine.Pin,
	dataBuffer DataBuffer,
	afterSoftwareResetFn func(b *BNO08X) tinygotypes.ErrorCode,
	options *SPIOptions,
) (*SPI, tinygotypes.ErrorCode) {
	// Check if the SPI bus is nil
	if spiBus == nil {
		return nil, ErrorCodeBNO08XNilSPIBus
	}

	// Configure CS pin as output and high
	csPin.Configure(machine.PinConfig{Mode: machine.PinOutput})
	csPin.High()

	// Configure INT pin as input
	intPin.Configure(machine.PinConfig{Mode: machine.PinInput})

	// Set PS0 pin to output and high
	ps0Pin.Configure(machine.PinConfig{Mode: machine.PinOutput})
	ps0Pin.High()

	// Set PS1 pin to output and high
	ps1Pin.Configure(machine.PinConfig{Mode: machine.PinOutput})
	ps1Pin.High()

	// Configure SPI
	if err := spiBus.Configure(
		machine.SPIConfig{
			Frequency: SPIFrequency,
			LSBFirst:  false,
			Mode:      SPIMode,
			SCK:       sckPin,
			SDO:       mosiPin,
			SDI:       misoPin,
		},
	); err != nil {
		return nil, ErrorCodeBNO08XFailedToConfigureSPI
	}

	// If options are nil, initialize with default values
	if options == nil {
		options = NewSPIOptions(nil, false)
	}

	// Get the debugger from options
	debugger := options.Options.Debugger

	// Create packet reader and writer
	packetReader, err := newSPIPacketReader(
		spiBus,
		intPin,
		dataBuffer,
		debugger,
		options.UltraDebug,
	)
	if err != nil {
		return nil, ErrorCodeBNO08XFailedToCreatePacketReader
	}

	packetWriter, err := newSPIPacketWriter(
		spiBus,
		dataBuffer,
		debugger,
		options.UltraDebug,
	)
	if err != nil {
		return nil, ErrorCodeBNO08XFailedToCreatePacketWriter
	}

	// Initialize BNO08X
	bno08x, err := NewBNO08X(
		resetPin,
		packetReader,
		packetWriter,
		dataBuffer,
		nil,
		afterSoftwareResetFn,
		options.Options,
	)
	if err != nil {
		return nil, ErrorCodeBNO08XFailedToCreateBNO08X
	}

	return &SPI{
		BNO08X:   bno08x,
		spiBus:   spiBus,
		ps1Pin:   ps1Pin,
		ps0Pin:   ps0Pin,
		resetPin: resetPin,
	}, nil
}

// GetBNO08X returns the BNO08X instance.
//
// Returns:
//
// The BNO08X instance.
func (spi *SPI) GetBNO08X() *BNO08X {
	return spi.BNO08X
}

// newSPIPacketReader creates a new SPIPacketReader instance.
//
// Parameters:
//
// spiBus: The SPI bus to use for communication.
// intPin: The INT pin to monitor for data readiness.
// debugger: The debugger to use for logging and debugging information.
// dataBuffer: The data buffer to use for storing Packet data.
// ultraDebug: Flag to enable ultra debug mode (optional).
//
// Returns:
//
// A pointer to a new SPIPacketReader instance.
func newSPIPacketReader(
	spiBus *machine.SPI,
	intPin machine.Pin,
	dataBuffer DataBuffer,
	debugger Debugger,
	ultraDebug bool,
) (*SPIPacketReader, tinygotypes.ErrorCode) {
	// Check if the SPI bus is nil
	if spiBus == nil {
		return nil, ErrorCodeBNO08XNilSPIBus
	}

	// Check if the dataBuffer is provided
	if dataBuffer == nil {
		return nil, ErrorCodeBNO08XNilDataBuffer
	}

	return &SPIPacketReader{
		spiBus:     spiBus,
		intPin:    intPin,
		debugger:   debugger,
		dataBuffer: dataBuffer,
		ultraDebug: ultraDebug,
	}, tinygotypes.ErrorCodeNil
}

// waitForInt waits for the INT pin to go low, indicating data is ready.
//
// Returns:
//
// An error if the wait times out.
func (pr *SPIPacketReader) waitForInt() tinygotypes.ErrorCode {
	if pr.debugger != nil {
		pr.debugger.Debug("Waiting for INT...")
	}

	startTime := time.Now()
	for time.Since(startTime) < SPIIntTimeout {
		if !pr.intPin.Get() {
			break
		}
	}
	return ErrorCodeBNO08XFailedToWakeUpSPI
}

// IsDataReady checks if data is available on SPI
//
// Returns:
//
// True if data is available, otherwise false.
func (pr *SPIPacketReader) IsDataReady() bool {
	if err := pr.waitForInt(); err != nil {
		return false
	}
	return true
}

// readHeader reads the Packet header from the SPI bus.
//
// Returns:
//
// A pointer to a PacketHeader or an error if reading the header fails.
func (pr *SPIPacketReader) readHeader() (*PacketHeader, tinygotypes.ErrorCode) {
	// Wait for INT pin to go low
	if err := pr.waitForInt(); err != tinygotypes.ErrorCodeNil {
		return nil, err
	}

	// Check if the destination slice is nil
	data := pr.dataBuffer.GetData()
	if data == nil {
		return nil, ErrorCodeBNO08XNilDestinationBuffer
	}

	// Check if start and end are within bounds
	if len(data) < PacketHeaderLength {
		return nil, ErrorCodeBNO08XDataBufferTooShortForPacketHeader
	}

	// Read the first 4 bytes from the SPI bus to get the Packet header.
	if err := pr.spiBus.Tx(
		nil,
		data[:PacketHeaderLength],
	); err != nil {
		return nil, err
	}

	header, err := NewPacketHeaderFromBuffer(data)
	if err != nil {
		return nil, err
	}

	// Debug log the header
	if pr.debugger != nil {
		pr.debugger.DebugBuffer(header.PrintBuffer(false))
	}
	return header, tinygotypes.ErrorCodeNil
}

// ReadPacket reads a Packet from the SPI bus.
//
// Returns:
//
// A pointer to a Packet or an error if reading the Packet fails.
func (pr *SPIPacketReader) ReadPacket() (*Packet, tinygotypes.ErrorCode) {
	// Read the Packet header
	header, err := pr.readHeader()
	if err != nil {
		return nil, err
	}

	// Validate header fields
	if header.PacketByteCount < PacketHeaderLength {
		return nil, ErrorCodeBNO08XInvalidPacketSize
	}

	// Extract header fields
	packetByteCount := header.PacketByteCount
	channelNumber := header.ChannelNumber
	sequenceNumber := header.SequenceNumber

	// Set sequence number in data buffer
	if err = pr.dataBuffer.SetSequenceNumber(
		channelNumber,
		sequenceNumber,
	); err != nil {
		return nil, err
	}

	// Skip header-only / empty packets
	if header.PacketByteCount == PacketHeaderLength || header.DataLength == 0 {
		if pr.debugger != nil {
			pr.debugger.Debug("Header-only packet received; skipping read")
		}
		return nil, ErrorCodeBNO08XNoPacketAvailable
	}

	// packetByteCount includes 4 header bytes
	payloadLength := packetByteCount - PacketHeaderLength

	if pr.debugger != nil {
		pr.debugger.Debug("Reading " + strconv.Itoa(payloadLength) + " bytes from SPI bus")
	}

	// Check if data buffer is large enough
	data := pr.dataBuffer.GetData()
	if len(data) < packetByteCount {
		// Resize data buffer and copy existing data
		newBuf := make([]byte, packetByteCount)
		copy(
			newBuf[:len(data)],
			data[:len(data)],
		)

		// Update data buffer reference
		pr.dataBuffer.SetData(data)

		if pr.debugger != nil {
			pr.debugger.Debug("Resized data buffer to " + strconv.Itoa(packetByteCount) + " bytes")
		}
	}

	// Preserve first 4 header bytes already read; read payload into slice after header.
	if payloadLength > 0 {
		if err := pr.spiBus.Tx(
			nil,
			data[PacketHeaderLength:packetByteCount],
		); err != nil {
			return ErrorCodeBNO08XSPIFailedToReadRequestedDataLength
		}
	}

	// Create a full Packet from the data buffer
	packet, err := NewPacketFromBuffer(pr.dataBuffer.GetData())
	if err != tinygotypes.ErrorCodeNil {
		return nil, err
	}

	// Debug log the packet
	if pr.debugger != nil {
		pr.debugger.DebugBuffer(packet.PrintBuffer(false))
	}

	// Update the sequence number in the data buffer
	if err = pr.dataBuffer.UpdateSequenceNumber(packet); err != nil {
		return nil, err
	}
	return packet, nil
}

// newSPIPacketWriter creates a new SPIPacketWriter instance.
//
// Parameters:
//
// spiBus: The SPI bus to use for communication.
// dataBuffer: The data buffer to use for storing Packet data.
// debugger: The debugger to use for logging and debugging information.
// ultraDebug: Flag to enable ultra debug mode (optional).
//
// Returns:
//
// A pointer to a new SPIPacketWriter instance, or an error if the dataBuffer is nil.
func newSPIPacketWriter(
	spiBus *machine.SPI,
	dataBuffer DataBuffer,
	debugger Debugger,
	ultraDebug bool,
) (*SPIPacketWriter, tinygotypes.ErrorCode) {
	// Check if the SPI bus is nil
	if spiBus == nil {
		return nil, ErrorCodeBNO08XNilSPIBus
	}

	// Check if the dataBuffer is provided
	if dataBuffer == nil {
		return nil, ErrorCodeBNO08XNilDataBuffer
	}

	return &SPIPacketWriter{
		spiBus:     spiBus,
		debugger:   debugger,
		dataBuffer: dataBuffer,
		ultraDebug: ultraDebug,
	}, tinygotypes.ErrorCodeNil
}

// SendPacket sends a packet over SPI, waiting for INT pin before sending.
//
// Parameters:
//
// channel: The channel to send the packet on.
// data: The data to send in the packet.
//
// Returns:
//
// The sequence number used and an error if any occurs.
func (pw *SPIPacketWriter) SendPacket(channel uint8, data []byte) (uint8, tinygotypes.ErrorCode) {
	// Check if the data is nil
	if data == nil {
		return 0, ErrorCodeBNO08XNilPacketData
	}

	// Get channel sequence number
	sequenceNumber, err := pw.dataBuffer.GetSequenceNumber(channel)
	if err != nil {
		return 0, err
	}

	// Initialize the packet from data
	packet, err := NewPacketFromData(
		channel,
		sequenceNumber,
		data,
	)
	if err != nil {
		return 0, err
	}

	// Debug log the packet
	if pw.debugger != nil {
		pw.debugger.DebugBuffer(packet.Header.PrintBuffer(true))
		pw.debugger.DebugBuffer(packet.PrintBuffer(true))
	}

	// Wait for INT pin to go low before sending
	if err := pw.waitForInt(); err != nil {
		return 0, err
	}

	// Write to SPI
	if err = pw.spiBus.Tx(packet.Header.Buffer, nil); err != nil {
		return sequenceNumber, ErrorCodeBNO08XSPIFailedToWritePacketHeaderBuffer
	}
	if err = pw.spiBus.Tx(packet.Data, nil); err != nil {
		return sequenceNumber, ErrorCodeBNO08XSPIFailedToWritePacketDataBuffer
	}

	// Update sequence number
	sequenceNumber, err = pw.dataBuffer.IncrementChannelSequenceNumber(channel)
	if err != nil {
		return 0, err
	}
	return sequenceNumber, nil
}