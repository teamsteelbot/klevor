package internal

type (
	// RoutineSignal is an enum to define the signal of a routine
	RoutineSignal uint8

	// RoutineStatus is an enum to define the status of a routine
	RoutineStatus uint8
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
