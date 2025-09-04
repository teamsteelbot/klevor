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
	OutgoingStatusOK
	OutgoingStatusHeartbeat
	OutgoingStatusStart
)

const (
	IncomingStatusNil IncomingStatus = iota
	IncomingStatusHeartbeat
	IncomingStatusOK
	IncomingStatusStop
)

var (
	// OutgoingStatusNames maps a given Status to its string name
	OutgoingStatusNames = map[OutgoingStatus]string{
		OutgoingStatusOK:        "ok",
		OutgoingStatusHeartbeat: "heartbeat",
		OutgoingStatusStart:     "start",
	}

	// IncomingStatusNames maps a given IncomingStatus to its string name
	IncomingStatusNames = map[IncomingStatus]string{
		IncomingStatusHeartbeat: "heartbeat",
		IncomingStatusOK:        "ok",
		IncomingStatusStop:      "stop",
	}
)

// String returns the string representation of the Status
//
// Returns:
//
// The string representation of the Status enum
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

// String returns the string representation of the IncomingStatus
//
// Returns:
//
// The string representation of the IncomingStatus enum
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
