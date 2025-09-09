//go:build tinygo && (rp2040 || rp2350)

package tinygo_bno08x

import (
	"fmt"
	"time"

	"machine"
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
	afterSoftwareResetFn func(b *BNO08X) error,
	options *SPIOptions,
) (*SPI, error) {
	// Check if the SPI bus is nil
	if spiBus == nil {
		return nil, ErrNilSPIBus
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
		return nil, fmt.Errorf("failed to configure spi: %w", err)
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
		return nil, fmt.Errorf("failed to create spi packet reader: %w", err)
	}

	packetWriter, err := newSPIPacketWriter(
		spiBus,
		dataBuffer,
		debugger,
		options.UltraDebug,
	)
	if err != nil {
		return nil, fmt.Errorf("failed to create spi packet writer: %w", err)
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
		return nil, fmt.Errorf("failed to initialize bno08x: %w", err)
	}

	return &SPI{
		BNO08X:   bno08x,
		spiBus:   spiBus,
		ps1Pin:   ps1Pin,
		ps0Pin:   ps0Pin,
		resetPin: resetPin,
	}, nil
}

// GetBNO08XService returns the BNO08X service.
//
// Returns:
//
// The BNO08X service instance.
func (spi *SPI) GetBNO08XService() BNO08XService {
	return spi.BNO08X
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
) (*SPIPacketReader, error) {
	// Check if the SPI bus is nil
	if spiBus == nil {
		return nil, ErrNilSPIBus
	}

	// Check if the dataBuffer is provided
	if dataBuffer == nil {
		return nil, ErrNilDataBuffer
	}

	return &SPIPacketReader{
		spiBus:     spiBus,
		intPin:    intPin,
		debugger:   debugger,
		dataBuffer: dataBuffer,
		ultraDebug: ultraDebug,
	}, nil
}

// waitForInt waits for the INT pin to go low, indicating data is ready.
//
// Returns:
//
// An error if the wait times out.
func (pr *SPIPacketReader) waitForInt() error {
	if pr.debugger != nil {
		pr.debugger.Debug("Waiting for INT...")
	}

	startTime := time.Now()
	for time.Since(startTime) < SPIIntTimeout {
		if !pr.intPin.Get() {
			break
		}
	}
	return ErrSPICouldNotBeWokenUp
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

// read reads a specified number of bytes from the I2C bus.
//
// Parameters:
//
// requestedReadLength: The number of bytes to read from the I2C bus.
//
// Returns:
//
// An error if reading from the I2C bus fails, otherwise nil.
func (pr *I2CPacketReader) read(requestedReadLength int) error {
	if pr.debugger != nil {
		pr.debugger.Debug(
			fmt.Sprintf(
				"Trying to read %d bytes",
				requestedReadLength,
			),
		)
	}

	// Full packet (header + payload)
	totalReadLength := requestedReadLength + PacketHeaderLength

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

		if pr.debugger != nil {
			pr.debugger.Debug(
				fmt.Printf(
					"Resized dataBuffer to %d bytes",
					totalReadLength,
				),
			)
		}
	}

	// Preserve first 4 header bytes already read; read payload into slice after header.
	if requestedReadLength > 0 {
		if err := pr.i2cBus.Tx(
			pr.address,
			nil,
			(*dataBufferPtr)[PacketHeaderLength:totalReadLength],
		); err != nil {
			return err
		}
	}
	return nil
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
func (pr *SPIPacketReader) readInto(dst *[]byte, start int, end *int) error {
	// Check if the data is ready
	if !pr.IsDataReady() {
		return ErrSPICouldNotBeWokenUp
	}

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
		b, err := pr.readByte()
		if err != nil {
			return err
		}
		if b == SPIControlEscape {
			nb, err := pr.readByte()
			if err != nil {
				return err
			}
			b = nb ^ 0x20
		}
		(*dst)[i] = b
	}
	return nil
}

/*
 def _read_into(self, buf, start=0, end=None):
        self._wait_for_int()

        with self._spi as spi:
            spi.readinto(buf, start=start, end=end, write_value=0x00)
        # print("SPI Read buffer (", end-start, "b )", [hex(i) for i in buf[start:end]])
*/

// readHeader reads the SPI packet header.
//
// Returns:
//
// An error if any occurs during reading.
func (pr *SPIPacketReader) readHeader() error {
	// Find first initial start byte
	for {
		b, err := pr.readByte()
		if err != nil {
			return err
		}
		if b == SPIStartAndEndByte {
			break
		}
	}

	// Read protocol ID sequence
	data, err := pr.readByte()
	if err != nil {
		return err
	}
	if data == SPIStartAndEndByte {
		// Consume next (real protocol byte)
		data, err = pr.readByte()
		if err != nil {
			return err
		}
	}
	if data != SPISHTPByte {
		return ErrUnhandledSPIControlSHTPProtocol
	}
	end := PacketHeaderLength

	return pr.readInto(pr.dataBuffer.GetData(), 0, &end)
}

// ReadPacket reads a packet from SPI
//
// Returns:
//
// A Packet object and an error if any occurs.
func (pr *SPIPacketReader) ReadPacket() (*Packet, error) {
	// Read packet header
	if err := pr.readHeader(); err != nil {
		return nil, err
	}

	// Parse header
	header, err := NewPacketHeaderFromBuffer(pr.dataBuffer.GetData())
	if err != nil {
		return nil, err
	}
	if header.PacketByteCount == 0 {
		return nil, ErrNoPacketAvailable
	}
	channelNumber := header.ChannelNumber

	// Check if the channel number is valid
	if channelNumber > MaxChannelNumber {
		return nil, ErrInvalidChannelNumber
	}

	// Check the data length for the packet
	if header.DataLength > MaxDataLength {
		return nil, fmt.Errorf(
			ErrInvalidDataLength,
			MaxDataLength,
			header.DataLength,
		)
	}

	// Debug log the header
	if pr.debugger != nil && pr.ultraDebug {
		headerStrPtr := header.String(false)
		if headerStrPtr != nil {
			pr.debugger.Debug(*headerStrPtr)
		} else {
			pr.debugger.Debug(ErrNilPacketHeaderString.Error())
		}

		// Log available bytes
		pr.debugger.Debug(
			fmt.Sprintf(
				"Channel %d has %d bytes available",
				channelNumber,
				header.PacketByteCount-PacketHeaderLength,
			),
		)
	}

	// Read remaining (payload) bytes
	end := int(header.PacketByteCount)
	dataBuffer := pr.dataBuffer.GetData()
	if err = pr.readInto(
		dataBuffer,
		PacketHeaderLength,
		&end,
	); err != nil {
		return nil, err
	}

	// Expect trailing 0x7E
	endByte, err := pr.readByte()
	if err != nil {
		return nil, err
	}
	if endByte != SPIStartAndEndByte {
		return nil, ErrSPIEndMissing
	}

	// Construct packet data
	packetData := make([]byte, header.DataLength)
	copy(packetData, (*dataBuffer)[PacketHeaderLength:header.PacketByteCount])

	// Initialize packet
	packet, err := NewPacket(&packetData, header)
	if err != nil {
		return nil, fmt.Errorf("failed to create packet from bytes: %w", err)
	}

	// Debug log the packet
	if pr.debugger != nil {
		packetStrPtr := packet.String(false)
		if packetStrPtr != nil {
			pr.debugger.Debug(*packetStrPtr)
		} else {
			pr.debugger.Debug(ErrNilPacketString.Error())
		}
	}

	// Update sequence number
	pr.dataBuffer.UpdateSequenceNumber(packet)
	return packet, nil
}


/*
   
    def _read_header(self):
        """Reads the first 4 bytes available as a header"""
        self._wait_for_int()

        # read header
        with self._spi as spi:
            spi.readinto(self._data_buffer, end=4, write_value=0x00)
        self._dbg("")
        self._dbg("SHTP READ packet header: ", [hex(x) for x in self._data_buffer[0:4]])

    def _read_packet(self):
        self._read_header()
        halfpacket = False

        print([hex(x) for x in self._data_buffer[0:4]])
        if self._data_buffer[1] & 0x80:
            halfpacket = True
        header = Packet.header_from_buffer(self._data_buffer)
        packet_byte_count = header.packet_byte_count
        channel_number = header.channel_number
        sequence_number = header.sequence_number

        self._sequence_number[channel_number] = sequence_number
        if packet_byte_count == 0:
            raise PacketError("No packet available")

        self._dbg("channel %d has %d bytes available" % (channel_number, packet_byte_count - 4))

        if packet_byte_count > DATA_BUFFER_SIZE:
            self._data_buffer = bytearray(packet_byte_count)

        # re-read header bytes since this is going to be a new transaction
        self._read_into(self._data_buffer, start=0, end=packet_byte_count)
        # print("Packet: ", [hex(i) for i in self._data_buffer[0:packet_byte_count]])

        if halfpacket:
            raise PacketError("read partial packet")
        new_packet = Packet(self._data_buffer)
        if self._debug:
            print(new_packet)
        self._update_sequence_number(new_packet)
        return new_packet

    def _read(self, requested_read_length):
        self._dbg("trying to read", requested_read_length, "bytes")
        unread_bytes = 0
        # +4 for the header
        total_read_length = requested_read_length + 4
        if total_read_length > DATA_BUFFER_SIZE:
            unread_bytes = total_read_length - DATA_BUFFER_SIZE
            total_read_length = DATA_BUFFER_SIZE

        with self._spi as spi:
            spi.readinto(self._data_buffer, end=total_read_length)
        return unread_bytes > 0

*/


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
) (*SPIPacketWriter, error) {
	// Check if the SPI bus is nil
	if spiBus == nil {
		return nil, ErrNilSPIBus
	}

	// Check if the dataBuffer is provided
	if dataBuffer == nil {
		return nil, ErrNilDataBuffer
	}

	return &SPIPacketWriter{
		spiBus:     spiBus,
		debugger:   debugger,
		dataBuffer: dataBuffer,
		ultraDebug: ultraDebug,
	}, nil
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
func (pw *SPIPacketWriter) SendPacket(channel uint8, data *[]byte) (uint8, error) {
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
		return 0, fmt.Errorf("failed to create packet: %w", err)
	}

	// Debug log the packet
	if pw.debugger != nil {
		packetStrPtr := packet.String(true)
		if packetStrPtr != nil {
			pw.debugger.Debug(*packetStrPtr)
		} else {
			pw.debugger.Debug(ErrNilPacketString.Error())
		}
	}

	// Get the packet buffer
	packetBufferPtr := packet.Buffer()
	if packetBufferPtr == nil {
		return 0, ErrNilPacketBuffer
	}

	// Wait for INT pin to go low before sending
	if err := pw.waitForInt(); err != nil {
		return 0, err
	}

	// Write packet to SPI
	for _, b := range *packetBufferPtr {
		if err := pw.spiBus.WriteByte(b); err != nil {
			return seqNum, err
		}
	}
    
	// Update sequence number
	sequenceNumber, err = pw.dataBuffer.IncrementChannelSequenceNumber(channel)
	if err != nil {
		return 0, err
	}
	return sequenceNumber, nil
}