//go:build tinygo && (rp2040 || rp2350)

package tinygo_bno08x

type (
	// DataBuffer is an interface for managing data buffers
	DataBuffer interface {
		GetData() *[]byte
		SetData(data *[]byte)
		ClearData()
		UpdateSequenceNumber(newPacket *Packet) error
		IncrementChannelSequenceNumber(channel uint8) (uint8, error)
		GetSequenceNumber(channel uint8) (uint8, error)
		SetSequenceNumber(channel uint8, sequenceNumber uint8) error
		IncrementReportSequenceNumber(reportID uint8)
		GetReportSequenceNumber(reportID uint8) uint8
		ResetSequenceNumbers()
	}

	// DefaultDataBuffer is a default implementation of the DataBuffer interface
	DefaultDataBuffer struct {
		data                    *[]byte
		sequenceNumber          []uint8
		reportsSequenceNumbers map[uint8]uint8
	}
)

// NewDefaultDataBuffer creates a new DefaultDataBuffer instance
func NewDefaultDataBuffer() *DefaultDataBuffer {
	// Initialize the data buffer with a size of DataBufferSize
	data := make([]byte, DataBufferSize)

	return &DefaultDataBuffer{
		data:                    &data,
		sequenceNumber:          make([]uint8, MaxChannelNumber),
		reportsSequenceNumbers: make(map[uint8]uint8),
	}
}

// GetData returns the data buffer
//
// Returns:
//
// A pointer to the byte slice representing the data buffer.
func (db *DefaultDataBuffer) GetData() *[]byte {
	return db.data
}

// SetData sets the data buffer
//
// Parameters:
//
//	data: A pointer to the byte slice to set as the data buffer. If nil, the data buffer is cleared.
func (db *DefaultDataBuffer) SetData(data *[]byte) {
	if data == nil {
		db.ClearData()
	} else {
		db.data = data
	}
}

// ClearData clears the data buffer
func (db *DefaultDataBuffer) ClearData() {
	// If the data buffer is nil, do nothing
	if db.data == nil {
		return
	}

	for i := range *db.data {
		(*db.data)[i] = 0
	}
}

// validateChannelNumber validates the channel number
//
// Parameters:
//
//	channel: The channel number to validate.
//
// Returns:
//
//	An error if the channel number is invalid, otherwise nil.
func (db *DefaultDataBuffer) validateChannelNumber(channel uint8) error {
	if int(channel) < 0 || int(channel) >= len(db.sequenceNumber) {
		return ErrInvalidChannelNumber
	}
	return nil
}

// UpdateSequenceNumber updates the cached sequence number for the given channel using the provided Packet.
//
// Parameters:
//
//	newPacket: A pointer to the Packet containing the channel and sequence number.
//
// Returns:
//
//	An error if the sequence number could not be updated, otherwise nil.
func (db *DefaultDataBuffer) UpdateSequenceNumber(newPacket *Packet) error {
	// Check if the packet is nil
	if newPacket == nil {
		return ErrNilPacket
	}

	// Check if the packet header is nil
	if newPacket.Header == nil {
		return ErrNilPacketHeader
	}

	// Get the channel number and sequence number from the packet
	channel := newPacket.ChannelNumber()
	seq := newPacket.Header.SequenceNumber

	// Validate the channel number
	if err := db.validateChannelNumber(channel); err != nil {
		return err
	}

	// Update the sequence number for the channel
	db.sequenceNumber[int(channel)] = seq
	return nil
}

// IncrementChannelSequenceNumber increments the sequence number for the given channel by the specified amount.
// It wraps at 256.
//
// Parameters:
//
//	channel: The channel for which to increment the sequence number.
//
// Returns:
//
//	The new sequence number for the channel, or an error if the channel is invalid.
func (db *DefaultDataBuffer) IncrementChannelSequenceNumber(channel uint8) (
	uint8,
	error,
) {
	// Validate the channel number
	if err := db.validateChannelNumber(channel); err != nil {
		return 0, err
	}

	// Increment the sequence number and wrap at 256
	newSequenceNumber := db.sequenceNumber[int(channel)] + 1
	db.sequenceNumber[int(channel)] = newSequenceNumber
	return newSequenceNumber, nil
}

// GetSequenceNumber returns the cached sequence number for the given channel.
//
// Parameters:
//
//	channel: The channel for which to get the sequence number.
//
// Returns:
//
//	The cached sequence number for the channel, or -1 if the channel is invalid.
func (db *DefaultDataBuffer) GetSequenceNumber(channel uint8) (uint8, error) {
	// Validate the channel number
	if err := db.validateChannelNumber(channel); err != nil {
		return 0, err
	}

	// Return the sequence number for the channel
	return db.sequenceNumber[int(channel)], nil
}

// SetSequenceNumber sets the cached sequence number for the given channel.
//
// Parameters:
//
//	channel: The channel for which to set the sequence number.
//	sequenceNumber: The sequence number to set for the channel.
//
// Returns:
//
// An error if the channel is invalid, otherwise nil.
func (db *DefaultDataBuffer) SetSequenceNumber(
	channel uint8,
	sequenceNumber uint8,
) error {
	// Validate the channel number
	if err := db.validateChannelNumber(channel); err != nil {
		return err
	}

	// Set the sequence number for the channel
	db.sequenceNumber[int(channel)] = sequenceNumber
	return nil
}

// IncrementReportSequenceNumber increments the sequence number for the given report ID, wrapping at 256.
//
// Parameters:
//
//	reportID: The ID of the report for which to increment the sequence number.
func (db *DefaultDataBuffer) IncrementReportSequenceNumber(reportID uint8) {
	current, ok := db.reportsSequenceNumbers[reportID]
	if !ok {
		current = 0
	}
	db.reportsSequenceNumbers[reportID] = current + 1
}

// GetReportSequenceNumber returns the current sequence number for the given report ID.
//
// Parameters:
//
//	reportID: The ID of the report for which to get the sequence number.
//
// Returns:
//
//	The current sequence number for the report ID.
func (db *DefaultDataBuffer) GetReportSequenceNumber(reportID uint8) uint8 {
	sequenceNumber, ok := db.reportsSequenceNumbers[reportID]
	if !ok {
		db.reportsSequenceNumbers[reportID] = 0
		return 0
	}
	return sequenceNumber
}

// ResetSequenceNumbers resets sequence numbers
func (db *DefaultDataBuffer) ResetSequenceNumbers() {
	db.sequenceNumber = make([]uint8, MaxChannelNumber)
	db.reportsSequenceNumbers = make(map[uint8]uint8)
}
