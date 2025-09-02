package enums

import (
	"fmt"
	"strings"
)

type (
	// Status represents the enum status messages sent and received to the Raspberry Pi 5
	Status uint8
)

const (
	StatusNil Status = iota
	StatusStart
	StatusStop
	StatusOK
	StatusHeartbeat
)

var (
	// StatusNames maps a given Status to its string name
	StatusNames = map[Status]string{
		StatusStart:     "start",
		StatusStop:      "stop",
		StatusOK:        "ok",
		StatusHeartbeat: "heartbeat",
	}
)

// String returns the string representation of the Status
//
// Returns:
//
// The string representation of the Status enum
func (s Status) String() string {
	return StatusNames[s]
}

// StatusFromString returns the Status enum based on a given string
//
// Parameters:
//
// s: The string name to search on StatusNames
//
// Returns:
//
// The Status enum value, or an error if the key wasn't found for the given value
func StatusFromString(s string) (Status, error) {
	// Format the string
	s = strings.ToLower(strings.TrimSpace(s))

	// Search for the given status name
	for key, value := range StatusNames {
		if value == s {
			return key, nil
		}
	}
	return StatusNil, fmt.Errorf(ErrInvalidStatusName, s)
}
