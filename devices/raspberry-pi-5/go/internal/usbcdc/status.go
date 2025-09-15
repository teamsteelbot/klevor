package usbcdc

import (
	"fmt"
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
	OutgoingStatusStop
)

const (
	IncomingStatusNil IncomingStatus = iota
	IncomingStatusHeartbeat
	IncomingStatusOK
	IncomingStatusStart
)

var (
	// OutgoingStatusNames maps a given OutgoingStatus to its string name
	OutgoingStatusNames = map[OutgoingStatus]string{
		OutgoingStatusOK:        "ok",
		OutgoingStatusHeartbeat: "heartbeat",
		OutgoingStatusStop:      "stop",
	}

	// IncomingStatusNames maps a given IncomingStatus to its string name
	IncomingStatusNames = map[IncomingStatus]string{
		IncomingStatusHeartbeat: "heartbeat",
		IncomingStatusOK:        "ok",
		IncomingStatusStart:     "start",
	}

	// OutgoingStatuses maps a given uint8 value to its OutgoingStatus enum
	OutgoingStatuses = map[uint8]OutgoingStatus{
		uint8(OutgoingStatusNil): OutgoingStatusNil,
		uint8(OutgoingStatusOK):  OutgoingStatusOK,
		uint8(OutgoingStatusHeartbeat): OutgoingStatusHeartbeat,
		uint8(OutgoingStatusStop):    OutgoingStatusStop,
	}

	// IncomingStatuses maps a given uint8 value to its IncomingStatus enum
	IncomingStatuses = map[uint8]IncomingStatus{
		uint8(IncomingStatusNil):      IncomingStatusNil,
		uint8(IncomingStatusHeartbeat): IncomingStatusHeartbeat,
		uint8(IncomingStatusOK):       IncomingStatusOK,
		uint8(IncomingStatusStart):    IncomingStatusStart,
	}
)

// String returns the name of the OutgoingStatus
//
// Returns:
//
// The name of the OutgoingStatus enum
func (o OutgoingStatus) String() string {
	return OutgoingStatusNames[o]
}

// Bytes returns the byte slice representation of the OutgoingStatus
//
// Returns:
//
// The byte slice representation of the OutgoingStatus enum
func (o OutgoingStatus) Bytes() []byte {
	return []byte{uint8(o)}
}

// OutgoingStatusFromUint8 returns the OutgoingStatus enum based on a given uint8 value
//
// Parameters:
//
// value: The uint8 value to search on OutgoingStatuss
//
// Returns:
//
// The OutgoingStatus enum value, or an error if the key wasn't found for the given value
func OutgoingStatusFromUint8(value uint8) (OutgoingStatus, error) {
	category, ok := OutgoingStatuses[value]
	if !ok {
		return OutgoingStatusNil, fmt.Errorf(ErrUnknownOutgoingStatus, value)
	}
	return category, nil
}

// OutgoingStatusFromBytes returns the OutgoingStatus enum based on a given byte slice
//
// Parameters:
//
// data: The byte slice to parse as OutgoingStatus
//
// Returns:
//
// The OutgoingStatus enum value, or an error if the key wasn't found for the given value
func OutgoingStatusFromBytes(data []byte) (OutgoingStatus, error) {
	if len(data) < 1 {
		return OutgoingStatusNil, ErrNilOutgoingStatus
	}
	return OutgoingStatusFromUint8(data[0])
}

// String returns the name of the IncomingStatus
//
// Returns:
//
// The name of the IncomingStatus enum
func (i IncomingStatus) String() string {
	return IncomingStatusNames[i]
}

// Bytes returns the byte slice representation of the IncomingStatus
//
// Returns:
//
// The byte slice representation of the IncomingStatus enum
func (i IncomingStatus) Bytes() []byte {
	return []byte{uint8(i)}
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
func IncomingStatusFromUint8(value uint8) (IncomingStatus, error) {
	category, ok := IncomingStatuses[value]
	if !ok {
		return IncomingStatusNil, fmt.Errorf(ErrUnknownIncomingStatus, value)
	}
	return category, nil
}

// IncomingStatusFromBytes returns the IncomingStatus enum based on a given byte slice
//
// Parameters:
//
// data: The byte slice to parse as IncomingStatus
//
// Returns:
//
// The IncomingStatus enum value, or an error if the key wasn't found for the given value
func IncomingStatusFromBytes(data []byte) (IncomingStatus, error) {
	if len(data) < 1 {
		return IncomingStatusNil, ErrNilIncomingStatus
	}
	return IncomingStatusFromUint8(data[0])
}