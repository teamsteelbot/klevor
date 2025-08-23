//go:build tinygo && (rp2040 || rp2350)

package test

import (
	"fmt"
	"time"

	"machine"
)

type (
	// I2C is the I2C implementation of the BNO08X sensor.
	I2C struct {
		BNO08X
		i2cBus  *machine.I2C
		address uint16
	}

	// I2CPacketReader represents the Packet reader for the I2C interface.
	I2CPacketReader struct {
		i2cBus       *machine.I2C
		dataBuffer   DataBuffer
		debugger     Debugger
		address      uint16 // I2C address of the device
		cachedHeader *PacketHeader
	}

	// I2CPacketWriter represents the Packet writer for the I2C interface.
	I2CPacketWriter struct {
		i2cBus     *machine.I2C
		dataBuffer DataBuffer
		debugger   Debugger
		address    uint16 // I2C address of the device
	}

	// I2COptions struct for configuring the BNO08X over I2C.
	I2COptions struct {
		Options  *Options
		Address0 *machine.Pin
	}
)

// probeDevice tries a zero-length write then a 1-byte read to confirm presence.
func probeDevice(bus *machine.I2C, addr uint16) error {
	// Zero-length write (some devices NACK this; tolerate)
	_ = bus.Tx(addr, nil, nil)

	// Attempt to read 1 byte (BNO08X will usually NACK but if wiring wrong we get generic error)
	buf := make([]byte, 1)
	if err := bus.Tx(addr, nil, buf); err != nil {
		return fmt.Errorf("probe failed at 0x%X: %w", addr, err)
	}
	return nil
}

// NewI2COptions creates a new I2COptions instance with default values.
//
// Parameters:
//
// debugger: The debugger to use for logging and debugging information (optional).
// resetPin: The pin used to reset the BNO08X sensor (optional).
// address0Pin: The pin used to set the I2C address (optional).
func NewI2COptions(
	debugger Debugger,
	resetPin *machine.Pin,
	address0Pin *machine.Pin,
) *I2COptions {
	return &I2COptions{
		Options:  NewOptions(debugger, resetPin),
		Address0: address0Pin,
	}
}

// NewI2C creates a new I2C instance for the BNO08X sensor.
//
// Parameters:
//
// i2cBus: The I2C bus to use for communication.
// sdaPin: The SDA pin for the I2C bus.
// sclPin: The SCL pin for the I2C bus.
// address: The I2C address of the BNO08X sensor.
// packetReader: The I2CPacketReader to use for reading Packets.
// packetWriter: The I2CPacketWriter to use for writing Packets.
// dataBuffer: The DataBuffer to use for storing Packet data.
// options: Optional configuration options for the BNO08X sensor.
//
// Returns:
//
// A pointer to a new I2C instance or an error if initialization fails.
func NewI2C(
	i2cBus *machine.I2C,
	sdaPin machine.Pin,
	sclPin machine.Pin,
	address uint16,
	dataBuffer DataBuffer,
	options *I2COptions,
) (*I2C, error) {
	// Check if the I2C bus is nil
	if i2cBus == nil {
		return nil, ErrNilI2CBus
	}

	// Configure the I2C bus
	if err := i2cBus.Configure(
		machine.I2CConfig{
			SCL:       sclPin,
			SDA:       sdaPin,
			Frequency: I2CFrequency,
		},
	); err != nil {
		return nil, fmt.Errorf("i2c configure: %w", err)
	}

	// Allow sensor boot time (adjust if you have an external reset just issued)
	time.Sleep(I2CSetupDelay)

	// Check if the address is the default or the alternative
	if address != I2CDefaultAddress && address != I2CAlternativeAddress {
		return nil, ErrInvalidI2CAddress
	}

	// Set the Address0 pin based on the desired address
	if options != nil && options.Address0 != nil {
		options.Address0.Configure(machine.PinConfig{Mode: machine.PinOutput})
		if address == I2CAlternativeAddress {
			options.Address0.High()
		} else {
			options.Address0.Low()
		}
	}

	// Probe with retries
	var lastErr error
	for i := 0; i < I2CProbeDeviceAttempts; i++ {
		if err := probeDevice(i2cBus, address); err != nil {
			lastErr = err
			time.Sleep(I2CProbeDeviceDelay)
			continue
		}
		lastErr = nil
		break
	}
	if lastErr != nil {
		// Option: comment this return to ignore probe failure and continue
		return nil, fmt.Errorf(
			"i2c probe (after %d attempts) failed: %w",
			I2CProbeDeviceAttempts,
			lastErr,
		)
	}

	// Get the debugger from options
	var debugger Debugger
	if options != nil {
		debugger = options.Options.Debugger
	}

	// Initialize the packet reader
	packetReader, err := newI2CPacketReader(
		i2cBus,
		address,
		dataBuffer,
		debugger,
	)
	if err != nil {
		return nil, fmt.Errorf("failed to create I2CPacketReader: %w", err)
	}

	// Initialize the packet writer
	packetWriter, err := newI2CPacketWriter(
		i2cBus,
		address,
		dataBuffer,
		debugger,
	)
	if err != nil {
		return nil, fmt.Errorf("failed to create I2CPacketWriter: %w", err)
	}

	// Initialize the BNO08X sensor
	bno08x, err := NewBNO08X(
		packetReader,
		packetWriter,
		dataBuffer,
		options.Options,
	)
	if err != nil {
		return nil, fmt.Errorf("failed to initialize BNO08X: %w", err)
	}

	return &I2C{
		BNO08X:  *bno08x,
		i2cBus:  i2cBus,
		address: address,
	}, nil
}

// newI2CPacketWriter creates a new I2CPacketWriter instance.
//
// Parameters:
//
// i2cBus: The I2C bus to use for communication.
// address: The I2C address of the device to read from.
// dataBuffer: The data buffer to use for storing Packet data.
// debugger: The debugger to use for logging and debugging information.
//
// Returns:
//
// A pointer to a new I2CPacketWriter instance, or an error if the dataBuffer is nil.
func newI2CPacketWriter(
	i2cBus *machine.I2C,
	address uint16,
	dataBuffer DataBuffer,
	debugger Debugger,
) (*I2CPacketWriter, error) {
	// Check if the I2C bus is nil
	if i2cBus == nil {
		return nil, ErrNilI2CBus
	}

	// Check if the dataBuffer is provided
	if dataBuffer == nil {
		return nil, ErrNilDataBuffer
	}

	return &I2CPacketWriter{
		i2cBus:     i2cBus,
		dataBuffer: dataBuffer,
		debugger:   debugger,
		address:    address,
	}, nil
}

// debug is a helper function to log debug messages if debugging is enabled.
//
// Parameters:
//
// args: The arguments to log as debug messages.
func (pw I2CPacketWriter) debug(args ...interface{}) {
	if pw.debugger != nil {
		pw.debugger.Debug(args...)
	}
}

// SendPacket sends a Packet over I2C.
//
// Parameters:
//
// channel: The channel number to send the Packet on.
// data: The data to send in the Packet.
//
// Returns:
//
// The sequence number of the Packet sent, or an error if sending fails.
func (pw I2CPacketWriter) SendPacket(channel uint8, data []byte) (
	uint8,
	error,
) {
	dataLength := len(data)
	writeLength := dataLength + 4

	// Ensure buffer is large enough
	dataBuffer := *pw.dataBuffer.GetData()
	if len(dataBuffer) < writeLength {
		dataBuffer = make([]byte, writeLength)
		pw.dataBuffer.SetData(&dataBuffer)
	}

	// Pack header: first two bytes are writeLength (little-endian)
	dataBuffer[0] = uint8(writeLength & 0xFF)
	dataBuffer[1] = uint8((writeLength >> 8) & 0xFF)
	dataBuffer[2] = channel
	sequenceNumber, err := pw.dataBuffer.GetSequenceNumber(channel)
	if err != nil {
		return 0, err
	}
	dataBuffer[3] = sequenceNumber

	// Copy data into buffer
	copy(dataBuffer[4:], data)

	// Create a new Packet from the data buffer
	dataBufferWriteLength := make([]byte, writeLength)
	copy(dataBufferWriteLength, dataBuffer[:writeLength])
	packet, err := NewPacket(&dataBufferWriteLength)
	if err != nil {
		return sequenceNumber, fmt.Errorf("failed to create Packet: %w", err)
	}

	// Debug log the packet
	packetStrPtr := packet.String(true)
	if packetStrPtr != nil {
		pw.debug(*packetStrPtr)
	} else {
		pw.debug("ERROR: nil packet string")
	}

	// Write to I2C
	if err = pw.i2cBus.Tx(pw.address, dataBufferWriteLength, nil); err != nil {
		return sequenceNumber, err
	}

	// Update sequence number
	sequenceNumber, err = pw.dataBuffer.IncrementChannelSequenceNumber(channel)
	if err != nil {
		return 0, err
	}
	return sequenceNumber, nil
}

// newI2CPacketReader creates a new I2CPacketReader instance.
//
// Parameters:
//
// i2cBus: The I2C bus to use for communication.
// debugger: The debugger to use for logging and debugging information.
// dataBuffer: The data buffer to use for storing Packet data.
// address: The I2C address of the device to read from.
//
// Returns:
//
// A pointer to a new I2CPacketReader instance.
func newI2CPacketReader(
	i2cBus *machine.I2C,
	address uint16,
	dataBuffer DataBuffer,
	debugger Debugger,
) (*I2CPacketReader, error) {
	// Check if the I2C bus is nil
	if i2cBus == nil {
		return nil, ErrNilI2CBus
	}

	// Check if the dataBuffer is provided
	if dataBuffer == nil {
		return nil, ErrNilDataBuffer
	}

	return &I2CPacketReader{
		i2cBus:     i2cBus,
		debugger:   debugger,
		dataBuffer: dataBuffer,
		address:    address,
	}, nil
}

// debug is a helper function to log debug messages if debugging is enabled.
//
// Parameters:
//
// args: The arguments to log as debug messages.
func (pr I2CPacketReader) debug(args ...any) {
	if pr.debugger != nil {
		pr.debugger.Debug(args...)
	}
}

// readHeader reads the Packet header from the I2C bus.
//
// Returns:
//
// A pointer to a PacketHeader or an error if reading the header fails.
func (pr I2CPacketReader) readHeader() (*PacketHeader, error) {
	// Read the first 4 bytes from the I2C bus to get the Packet header.
	if err := pr.i2cBus.Tx(
		pr.address,
		nil,
		(*pr.dataBuffer.GetData())[:4],
	); err != nil {
		return nil, err
	}

	header, err := NewPacketHeader(pr.dataBuffer.GetData())
	if err != nil {
		return nil, err
	}

	// Debug log the header
	/*
		headerStrPtr := header.String(false)
		if headerStrPtr != nil {
			pr.debug(*headerStrPtr)
		} else {
			pr.debug("ERROR: nil header string")
		}
	*/
	return header, nil
}

// nextHeader reads the next Packet header, using a cached header if available.
//
// Returns:
//
// A pointer to a PacketHeader or an error if reading the header fails.
func (pr I2CPacketReader) nextHeader() (*PacketHeader, error) {
	if pr.cachedHeader != nil {
		header := pr.cachedHeader
		pr.cachedHeader = nil
		return header, nil
	}

	header, err := pr.readHeader()
	if err != nil {
		return nil, err
	}
	return header, nil
}

func (pr I2CPacketReader) ReadPacket() (*Packet, error) {
	// Get next header (cached or read new)
	header, err := pr.nextHeader()
	if err != nil {
		return nil, fmt.Errorf("failed to read header: %w", err)
	}

	// Validate header fields
	if header.PacketByteCount < 4 {
		return nil, fmt.Errorf("invalid packet size %d", header.PacketByteCount)
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
		return nil, fmt.Errorf("failed to set sequence number: %w", err)
	}

	// Skip header-only / empty packets
	if header.PacketByteCount == 4 || header.DataLength == 0 {
		pr.debug("Skipping empty packet on channel", header.ChannelNumber)
		return nil, ErrNoPacketAvailable
	}

	// packetByteCount includes 4 header bytes
	payloadLen := packetByteCount - 4
	pr.debug(
		fmt.Sprintf(
			"Channel %d has %d bytes available to read",
			channelNumber,
			payloadLen,
		),
	)

	// Read the remaining bytes of the Packet
	if err = pr.read(payloadLen); err != nil {
		return nil, fmt.Errorf("failed to read Packet data: %w", err)
	}

	// Create a full Packet from the data buffer
	newPacket, err := NewPacket(pr.dataBuffer.GetData())
	if err != nil {
		return nil, fmt.Errorf("failed to create Packet from bytes: %w", err)
	}

	// Debug log the packet
	newPacketStrPtr := newPacket.String(false)
	if newPacketStrPtr != nil {
		pr.debug(*newPacketStrPtr)
	} else {
		pr.debug("ERROR: nil packet string")
	}

	// Update the sequence number in the data buffer
	if err = pr.dataBuffer.UpdateSequenceNumber(newPacket); err != nil {
		return nil, fmt.Errorf("failed to update sequence number: %w", err)
	}

	// Clear the data buffer for next read
	// pr.dataBuffer.Clear()
	return newPacket, nil
}

// read reads a specified number of bytes from the I2C bus.
//
// Parameters:
//
// requestedReadLength: The number of bytes to read from the I2C bus.
//
// Returns:
//
// An error if reading from the I2C bus fails, otherwise nil.
func (pr I2CPacketReader) read(requestedReadLength int) error {
	pr.debug(fmt.Sprintf("Trying to read %d bytes", requestedReadLength))

	// Full packet (header + payload)
	totalReadLength := requestedReadLength + 4

	// Check if data buffer is large enough
	dataBufferPtr := pr.dataBuffer.GetData()
	if len(*dataBufferPtr) < totalReadLength {
		// Resize data buffer and copy existing data
		newBuf := make([]byte, totalReadLength)
		copy(
			newBuf[:len(*dataBufferPtr)],
			(*dataBufferPtr)[:len(*dataBufferPtr)],
		)

		// Update data buffer reference
		pr.dataBuffer.SetData(&newBuf)
		dataBufferPtr = &newBuf
		pr.debug(fmt.Printf("Resized dataBuffer to %d bytes", totalReadLength))
	}

	// Preserve first 4 header bytes already read; read payload into slice after header.
	if requestedReadLength > 0 {
		if err := pr.i2cBus.Tx(
			pr.address,
			nil,
			(*dataBufferPtr)[4:totalReadLength],
		); err != nil {
			return err
		}
	}
	return nil
}

// IsDataReady checks if there is data ready to be read from the I2C bus.
//
// Returns:
//
// True if data is ready, false otherwise. It also checks for errors in the header.
func (pr I2CPacketReader) IsDataReady() bool {
	// Check cached header first
	if pr.cachedHeader != nil {
		return pr.cachedHeader.PacketByteCount > 4 && pr.cachedHeader.DataLength > 0
	}

	header, err := pr.readHeader()
	if err != nil {
		pr.debug("ERROR: failed to read header: ", err)
		return false
	}
	if header.ChannelNumber > 5 {
		pr.debug("Channel number out of range: ", header.ChannelNumber)
	}
	if header.PacketByteCount == 0x7FFF {
		pr.debug("Byte count is 0x7FFF/0xFFFF; Error?")
		if header.SequenceNumber == 0xFF {
			pr.debug("Sequence number is 0xFF; Error?")
		}
		return false
	}
	pr.cachedHeader = header
	return header.PacketByteCount > 4 && header.DataLength > 0
}
