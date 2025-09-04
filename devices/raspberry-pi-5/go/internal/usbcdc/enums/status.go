package enums

import (
	"fmt"
	"strings"
)

type (
	// IncomingStatus represents the enum status messages received from to the Raspberry Pi Pico 2W
	IncomingStatus uint8

	// OutgoingStatus represents the enum status messages sent to the Raspberry Pi Pico 2W
	OutgoingStatus uint8
)

const (
	IncomingStatusNil IncomingStatus = iota
	IncomingStatusOK
	IncomingStatusHeartbeat
	IncomingStatusStart
)

const (
	OutgoingStatusNil OutgoingStatus = iota
	OutgoingStatusHeartbeat
	OutgoingStatusOK
	OutgoingStatusStop
)

var (
	// IncomingStatusNames maps a given Status to its string name
	IncomingStatusNames = map[IncomingStatus]string{
		IncomingStatusStart:     "start",
		IncomingStatusOK:        "ok",
		IncomingStatusHeartbeat: "heartbeat",
	}

	// OutgoingStatusNames maps a given OutgoingStatus to its string name
	OutgoingStatusNames = map[OutgoingStatus]string{
		OutgoingStatusHeartbeat: "heartbeat",
		OutgoingStatusOK:        "ok",
		OutgoingStatusStop:      "stop",
	}
)

// String returns the string representation of the Status
//
// Returns:
//
// The string representation of the Status enum
func (i IncomingStatus) String() string {
	return IncomingStatusNames[i]
}

// IncomingStatusFromString returns the IncomingStatus enum based on a given string
//
// Parameters:
//
// s: The string name to search on IncomingStatusNames
//
// Returns:
//
// The IncomingStatus enum value, or an error if the key wasn't found for the given value
func IncomingStatusFromString(s string) (IncomingStatus, error) {
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

// String returns the string representation of the OutgoingStatus
//
// Returns:
//
// The string representation of the OutgoingStatus enum
func (o OutgoingStatus) String() string {
	return OutgoingStatusNames[o]
}

// OutgoingStatusFromString returns the OutgoingStatus enum based on a given string
//
// Parameters:
//
// s: The string name to search on OutgoingStatusNames
//
// Returns:
//
// The OutgoingStatus enum value, or an error if the key wasn't found for the given value
func OutgoingStatusFromString(s string) (OutgoingStatus, error) {
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
