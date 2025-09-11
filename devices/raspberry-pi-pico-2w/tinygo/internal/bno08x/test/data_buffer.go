//go:build tinygo && (rp2040 || rp2350)

package tinygo_bno08x

import (
	tinygotypes "github.com/ralvarezdev/tinygo-types"
)

type (
	// DefaultDataBuffer is a default implementation of the DataBuffer interface
	DefaultDataBuffer struct {
		data                    []byte
		sequenceNumber          []uint8
		reportsSequenceNumbers [256]uint8
	}
)

// NewDefaultDataBuffer creates a new DefaultDataBuffer instance
func NewDefaultDataBuffer() *DefaultDataBuffer {
	return &DefaultDataBuffer{
		data:                    make([]byte, DataBufferSize),
		sequenceNumber:          make([]uint8, MaxChannelNumber),
		reportsSequenceNumbers: [256]uint8{},
	}
}

// GetData returns the data buffer
//
// Returns:
//
// A slice of bytes representing the data buffer.
func (db *DefaultDataBuffer) GetData() []byte {
	return db.data
}

// SetDataValue sets the data buffer value at the specified index
//
// Parameters:
//
//	index: The index in the data buffer to set the value.
//	value: The byte value to set at the specified index.
//
// Returns:
//
// An error if the index is out of range, otherwise nil.
func (db *DefaultDataBuffer) SetDataValue(index int, value byte) tinygotypes.ErrorCode {
	if index < 0 || index >= len(db.data) {
		return ErrorCodeBNO08XDataBufferIndexOutOfRange
	}
	db.data[index] = value
	return tinygotypes.ErrorCodeNil
}

// SetData sets the data buffer with the provided data slice
//
// Parameters:
//
//	data: The byte slice to set as the data buffer.
//
// Returns:
//
// An error if the data slice is nil or exceeds the buffer size, otherwise nil.
func (db *DefaultDataBuffer) SetData(data []byte) tinygotypes.ErrorCode {
	if data == nil {
		return ErrorCodeBNO08XNilDataBuffer
	}
	db.data = data
	return tinygotypes.ErrorCodeNil
}

// ClearData clears the data buffer
func (db *DefaultDataBuffer) ClearData() {
	for i := range db.data {
		db.data[i] = 0
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
func (db *DefaultDataBuffer) validateChannelNumber(channel uint8) tinygotypes.ErrorCode {
	if int(channel) < 0 || int(channel) >= len(db.sequenceNumber) {
		return ErrorCodeBNO08XInvalidChannelNumber
	}
	return tinygotypes.ErrorCodeNil
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
func (db *DefaultDataBuffer) UpdateSequenceNumber(newPacket *Packet) tinygotypes.ErrorCode {
	// Check if the packet is nil
	if newPacket == nil {
		return ErrorCodeBNO08XNilPacket
	}

	// Check if the packet header is nil
	if newPacket.Header == nil {
		return ErrorCodeBNO08XNilPacketHeader
	}

	// Get the channel number and sequence number from the packet
	channel := newPacket.ChannelNumber()
	seq := newPacket.Header.SequenceNumber

	// Validate the channel number
	if err := db.validateChannelNumber(channel); err != tinygotypes.ErrorCodeNil {
		return err
	}

	// Update the sequence number for the channel
	db.sequenceNumber[int(channel)] = seq
	return tinygotypes.ErrorCodeNil
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
	tinygotypes.ErrorCode,
) {
	// Validate the channel number
	if err := db.validateChannelNumber(channel); err != tinygotypes.ErrorCodeNil {
		return 0, err
	}

	// Increment the sequence number and wrap at 256
	newSequenceNumber := db.sequenceNumber[int(channel)] + 1
	db.sequenceNumber[int(channel)] = newSequenceNumber
	return newSequenceNumber, tinygotypes.ErrorCodeNil
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
func (db *DefaultDataBuffer) GetSequenceNumber(channel uint8) (uint8, tinygotypes.ErrorCode) {
	// Validate the channel number
	if err := db.validateChannelNumber(channel); err != tinygotypes.ErrorCodeNil {
		return 0, err
	}

	// Return the sequence number for the channel
	return db.sequenceNumber[int(channel)], tinygotypes.ErrorCodeNil
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
) tinygotypes.ErrorCode {
	// Validate the channel number
	if err := db.validateChannelNumber(channel); err != tinygotypes.ErrorCodeNil {
		return err
	}

	// Set the sequence number for the channel
	db.sequenceNumber[int(channel)] = sequenceNumber
	return tinygotypes.ErrorCodeNil
}

// IncrementReportSequenceNumber increments the sequence number for the given report ID, wrapping at 256.
//
// Parameters:
//
//	reportID: The ID of the report for which to increment the sequence number.
func (db *DefaultDataBuffer) IncrementReportSequenceNumber(reportID uint8) {
	db.reportsSequenceNumbers[reportID]++
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
	return db.reportsSequenceNumbers[reportID]
}

// ResetSequenceNumbers resets sequence numbers
func (db *DefaultDataBuffer) ResetSequenceNumbers() {
	// Reset the sequence numbers for all channels
	for i := range db.sequenceNumber {
		db.sequenceNumber[i] = 0
	}

	// Reset the sequence numbers for all reports
	for reportID := range db.reportsSequenceNumbers {
		db.reportsSequenceNumbers[reportID] = 0
	}
}
