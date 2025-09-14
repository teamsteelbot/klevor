package usbcdc

import (
	tinygotypes "github.com/ralvarezdev/tinygo-types"
)

type (
	// OutgoingStatus represents the enum status messages sent to the Raspberry Pi 5
	OutgoingStatus uint8

	// IncomingStatus represents the enum status messages received from the Raspberry Pi 5
	IncomingStatus uint8
)

const (
	OutgoingStatusNil OutgoingStatus = iota
	OutgoingStatusHeartbeat
	OutgoingStatusOK
	OutgoingStatusStart
)

const (
	IncomingStatusNil IncomingStatus = iota
	IncomingStatusHeartbeat
	IncomingStatusOK
	IncomingStatusStop
)

// OutgoingStatusFromUint8 returns the OutgoingStatus enum based on a given uint8 value
//
// Parameters:
//
// value: The uint8 value to search on OutgoingStatuss
//
// Returns:
//
// The OutgoingStatus enum value, or an error if the key wasn't found for the given value
func OutgoingStatusFromUint8(value uint8) (OutgoingStatus, tinygotypes.ErrorCode) {
	switch OutgoingStatus(value) {
	case OutgoingStatusNil:
		return OutgoingStatusNil, tinygotypes.ErrorCodeNil
	case OutgoingStatusHeartbeat:
		return OutgoingStatusHeartbeat, tinygotypes.ErrorCodeNil
	case OutgoingStatusOK:
		return OutgoingStatusOK, tinygotypes.ErrorCodeNil
	case OutgoingStatusStart:
		return OutgoingStatusStart, tinygotypes.ErrorCodeNil
	default:
		return OutgoingStatusNil, ErrorCodeUSBCDCUnknownOutgoingStatus
	}
}

// IncomingStatusFromUint8 returns the IncomingStatus enum based on a given uint8 value
//
// Parameters:
//
// value: The uint8 value to search on IncomingStatuss
//
// Returns:
//
// The IncomingStatus enum value, or an error if the key wasn't found for the given value
func IncomingStatusFromUint8(value uint8) (IncomingStatus, tinygotypes.ErrorCode) {
	switch IncomingStatus(value) {
	case IncomingStatusNil:
		return IncomingStatusNil, tinygotypes.ErrorCodeNil
	case IncomingStatusHeartbeat:
		return IncomingStatusHeartbeat, tinygotypes.ErrorCodeNil
	case IncomingStatusOK:
		return IncomingStatusOK, tinygotypes.ErrorCodeNil
	case IncomingStatusStop:
		return IncomingStatusStop, tinygotypes.ErrorCodeNil
	default:
		return IncomingStatusNil, ErrorCodeUSBCDCUnknownIncomingStatus
	}
}