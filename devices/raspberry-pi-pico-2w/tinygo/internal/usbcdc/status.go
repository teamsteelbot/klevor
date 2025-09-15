package usbcdc

import (
	tinygoerrors "github.com/ralvarezdev/tinygo-errors"
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
func OutgoingStatusFromUint8(value uint8) (OutgoingStatus, tinygoerrors.ErrorCode) {
	switch OutgoingStatus(value) {
	case OutgoingStatusNil:
		return OutgoingStatusNil, tinygoerrors.ErrorCodeNil
	case OutgoingStatusHeartbeat:
		return OutgoingStatusHeartbeat, tinygoerrors.ErrorCodeNil
	case OutgoingStatusOK:
		return OutgoingStatusOK, tinygoerrors.ErrorCodeNil
	case OutgoingStatusStart:
		return OutgoingStatusStart, tinygoerrors.ErrorCodeNil
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
func IncomingStatusFromUint8(value uint8) (IncomingStatus, tinygoerrors.ErrorCode) {
	switch IncomingStatus(value) {
	case IncomingStatusNil:
		return IncomingStatusNil, tinygoerrors.ErrorCodeNil
	case IncomingStatusHeartbeat:
		return IncomingStatusHeartbeat, tinygoerrors.ErrorCodeNil
	case IncomingStatusOK:
		return IncomingStatusOK, tinygoerrors.ErrorCodeNil
	case IncomingStatusStop:
		return IncomingStatusStop, tinygoerrors.ErrorCodeNil
	default:
		return IncomingStatusNil, ErrorCodeUSBCDCUnknownIncomingStatus
	}
}