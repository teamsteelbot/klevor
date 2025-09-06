package enums

import (
	"fmt"
	"strings"
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
		OutgoingStatusNil.Uint8(): OutgoingStatusNil,
		OutgoingStatusOK.Uint8():  OutgoingStatusOK,
		OutgoingStatusHeartbeat.Uint8(): OutgoingStatusHeartbeat,
		OutgoingStatusStop.Uint8():    OutgoingStatusStop,
	}

	// IncomingStatuses maps a given uint8 value to its IncomingStatus enum
	IncomingStatuses = map[uint8]IncomingStatus{
		IncomingStatusNil.Uint8():      IncomingStatusNil,
		IncomingStatusHeartbeat.Uint8(): IncomingStatusHeartbeat,
		IncomingStatusOK.Uint8():       IncomingStatusOK,
		IncomingStatusStart.Uint8():    IncomingStatusStart,
	}
)

// Uint8 returns the uint8 representation of the OutgoingStatus
//
// Returns:
//
// The uint8 representation of the OutgoingStatus enum
func (o OutgoingStatus) Uint8() uint8 {
	return uint8(o)
}

// Name returns the name of the OutgoingStatus
//
// Returns:
//
// The name of the OutgoingStatus enum
func (o OutgoingStatus) Name() string {
	return OutgoingStatusNames[o]
}

// String returns the string representation of the OutgoingStatus
//
// Returns:
//
// The string representation of the OutgoingStatus enum
func (o OutgoingStatus) String() string {
	return fmt.Sprintf("%d", o)
}

// OutgoingStatusByName returns the OutgoingStatus enum based on a given string
//
// Parameters:
//
// s: The string name to search on OutgoingStatusNames
//
// Returns:
//
// The OutgoingStatus enum value, or an error if the key wasn't found for the given value
func OutgoingStatusByName(s string) (OutgoingStatus, error) {
	// Format the string
	s = strings.ToLower(strings.TrimSpace(s))

	// Search for the given status name
	for key, value := range OutgoingStatusNames {
		if value == s {
			return key, nil
		}
	}
	return OutgoingStatusNil, fmt.Errorf(ErrInvalidOutgoingStatusName, s)
}

// OutgoingStatusFromString returns the OutgoingStatus enum based on a given string
//
// Parameters:
//
// s: The string to parse as OutgoingStatus
//
// Returns:
//
// The OutgoingStatus enum value, or an error if the key wasn't found for the given value
func OutgoingStatusFromString(s string) (OutgoingStatus, error) {
	// Format the string
	s = strings.ToLower(strings.TrimSpace(s))

	// Try to parse as uint8 first
	var value uint8
	if _, err := fmt.Sscanf(s, "%d", &value); err != nil {
		return OutgoingStatusNil, fmt.Errorf(ErrInvalidOutgoingStatusString, s)
	}

	// If the string was a number, try to get the OutgoingStatus from the uint8 value
	category, err := OutgoingStatusFromUint8(value);
	if err != nil {
		return OutgoingStatusNil, err
	}
	return category, nil
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
		return OutgoingStatusNil, fmt.Errorf(ErrInvalidOutgoingStatusUint8, value)
	}
	return category, nil
}

// Uint8 returns the uint8 representation of the IncomingStatus
//
// Returns:
//
// The uint8 representation of the IncomingStatus enum
func (i IncomingStatus) Uint8() uint8 {
	return uint8(i)
}

// Name returns the name of the IncomingStatus
//
// Returns:
//
// The name of the IncomingStatus enum
func (i IncomingStatus) Name() string {
	return IncomingStatusNames[i]
}

// String returns the string representation of the IncomingStatus
//
// Returns:
//
// The string representation of the IncomingStatus enum
func (i IncomingStatus) String() string {
	return fmt.Sprintf("%d", i)
}

// IncomingStatusByName returns the IncomingStatus enum based on a given string
//
// Parameters:
//
// s: The string name to search on IncomingStatusNames
//
// Returns:
//
// The IncomingStatus enum value, or an error if the key wasn't found for the given value
func IncomingStatusByName(s string) (IncomingStatus, error) {
	// Format the string
	s = strings.ToLower(strings.TrimSpace(s))

	// Search for the given status name
	for key, value := range IncomingStatusNames {
		if value == s {
			return key, nil
		}
	}
	return IncomingStatusNil, fmt.Errorf(ErrInvalidIncomingStatusName, s)
}

// IncomingStatusFromString returns the IncomingStatus enum based on a given string
//
// Parameters:
//
// s: The string to parse as IncomingStatus
//
// Returns:
//
// The IncomingStatus enum value, or an error if the key wasn't found for the given value
func IncomingStatusFromString(s string) (IncomingStatus, error) {
	// Format the string
	s = strings.ToLower(strings.TrimSpace(s))

	// Try to parse as uint8 first
	var value uint8
	if _, err := fmt.Sscanf(s, "%d", &value); err != nil {
		return IncomingStatusNil, fmt.Errorf(ErrInvalidIncomingStatusString, s)
	}

	// If the string was a number, try to get the IncomingStatus from the uint8 value
	category, err := IncomingStatusFromUint8(value);
	if err != nil {
		return IncomingStatusNil, err
	}
	return category, nil
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
		return IncomingStatusNil, fmt.Errorf(ErrInvalidIncomingStatusUint8, value)
	}
	return category, nil
}