package internal

import (
	"fmt"
	"strings"
)

type (
	// RoutineSignal is an enum to define the signal of a routine
	RoutineSignal uint8

	// RoutineStatus is an enum to define the status of a routine
	RoutineStatus uint8

	// PositiveLabel is an enum to define the label of a positive Hailo CLIP classification
	PositiveLabel uint8

	// NegativeLabel is an enum to define the label of a negative Hailo CLIP classification
	NegativeLabel uint8
)

const (
	RoutineSignalNil RoutineSignal = iota
	RoutineSignalStart
	RoutineSignalStop
)

const (
	RoutineStatusNil RoutineStatus = iota
	RoutineStatusWaitingToStart
	RoutineStatusRunning
	RoutineStatusStopped
	RoutineStatusError
)

const (
	PositiveLabelNil PositiveLabel = iota
	PositiveLabelGreenBlock
	PositiveLabelRedBlock
	PositiveLabelMagentaBlock
)

const (
	NegativeLabelNil NegativeLabel = iota
	NegativeLabelBackground
	NegativeLabelBlackBlock
)

var (
	// RoutineSignalNames maps a given RoutineSignal to its string name
	RoutineSignalNames = map[RoutineSignal]string{
		RoutineSignalStart: "START",
		RoutineSignalStop:  "STOP",
	}

	// RoutineStatusNames maps a given RoutineStatus to its string name
	RoutineStatusNames = map[RoutineStatus]string{
		RoutineStatusWaitingToStart: "WAITING_TO_START",
		RoutineStatusRunning:        "RUNNING",
		RoutineStatusStopped:        "STOPPED",
		RoutineStatusError:          "ERROR",
	}

	// PositiveLabelNames maps a given PositiveLabel to its string name
	PositiveLabelNames = map[PositiveLabel]string{
		PositiveLabelGreenBlock:   "green block",
		PositiveLabelRedBlock:     "red block",
		PositiveLabelMagentaBlock: "magenta block",
	}

	// NegativeLabelNames maps a given NegativeLabel to its string name
	NegativeLabelNames = map[NegativeLabel]string{
		NegativeLabelBackground: "background",
		NegativeLabelBlackBlock: "black block",
	}
)

// String returns the string representation of the RoutineSignal
//
// Returns:
//
// The string representation of the RoutineSignal enum
func (r RoutineSignal) String() string {
	return RoutineSignalNames[r]
}

// String returns the string representation of the RoutineStatus
//
// Returns:
//
// The string representation of the RoutineStatus enum
func (r RoutineStatus) String() string {
	return RoutineStatusNames[r]
}

// String returns the string representation of the PositiveLabel
//
// Returns:
//
// The string representation of the PositiveLabel enum
func (p PositiveLabel) String() string {
	return PositiveLabelNames[p]
}

// PositiveLabelFromString returns the PositiveLabel enum based on a given string
//
// Parameters:
//
// s: The string name to search on PositiveLabelNames
//
// Returns:
//
// The PositiveLabel enum value, or an error if the key wasn't found for the given value
func PositiveLabelFromString(s string) (PositiveLabel, error) {
	// Format the string
	s = strings.ToLower(strings.TrimSpace(s))

	// Search for the given positive label name
	for key, value := range PositiveLabelNames {
		if value == s {
			return key, nil
		}
	}
	return PositiveLabelNil, fmt.Errorf(ErrInvalidPositiveLabelName, s)
}

// String returns the string representation of the NegativeLabel
//
// Returns:
//
// The string representation of the NegativeLabel enum
func (n NegativeLabel) String() string {
	return NegativeLabelNames[n]
}
