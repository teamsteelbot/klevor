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

	// Challenge represents the enum challenge messages sent and received from the Raspberry Pi Pico
	Challenge uint8
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
	ChallengeNil Challenge = iota
	ChallengeWithoutObstacles
	ChallengeWithObstacles
	ChallengeWithObstaclesAndParking
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

	// ChallengeNames maps a given Challenge to its string name
	ChallengeNames = map[Challenge]string{
		ChallengeWithObstacles:           "with_obstacles",
		ChallengeWithoutObstacles:        "without_obstacles",
		ChallengeWithObstaclesAndParking: "with_obstacles_and_parking",
	}

	// Challenges maps a given uint8 value to its Challenge enum
	Challenges = map[uint8]Challenge{
		ChallengeNil.Uint8():                 ChallengeNil,
		ChallengeWithObstacles.Uint8():       ChallengeWithObstacles,
		ChallengeWithoutObstacles.Uint8():    ChallengeWithoutObstacles,
		ChallengeWithObstaclesAndParking.Uint8(): ChallengeWithObstaclesAndParking,
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

// Uint8 returns the uint8 representation of the Challenge
//
// Returns:
//
// The uint8 representation of the Challenge enum
func (c Challenge) Uint8() uint8 {
	return uint8(c)
}

// Name returns the name of the Challenge
//
// Returns:
//
// The name of the Challenge enum
func (c Challenge) Name() string {
	return ChallengeNames[c]
}

// String returns the string representation of the Challenge
//
// Returns:
//
// The string representation of the Challenge enum
func (c Challenge) String() string {
	return fmt.Sprintf("%d", c)
}

// ChallengeByName returns the Challenge enum based on a given string
//
// Parameters:
//
// s: The string name to search on ChallengeNames
//
// Returns:
//
// The Challenge enum value, or an error if the key wasn't found for the given value
func ChallengeByName(s string) (Challenge, error) {
	// Format the string
	s = strings.ToLower(strings.TrimSpace(s))

	// Search for the given challenge name
	for key, value := range ChallengeNames {
		if value == s {
			return key, nil
		}
	}
	return ChallengeNil, fmt.Errorf(ErrInvalidChallengeName, s)
}

// ChallengeFromString returns the Challenge enum based on a given string
//
// Parameters:
//
// s: The string to parse as Challenge
//
// Returns:
//
// The Challenge enum value, or an error if the key wasn't found for the given value
func ChallengeFromString(s string) (Challenge, error) {
	// Format the string
	s = strings.ToLower(strings.TrimSpace(s))

	// Try to parse as uint8 first
	var value uint8
	if _, err := fmt.Sscanf(s, "%d", &value); err != nil {
		return ChallengeNil, fmt.Errorf(ErrInvalidChallengeString, s)
	}

	// If the string was a number, try to get the Challenge from the uint8 value
	category, err := ChallengeFromUint8(value);
	if err != nil {
		return ChallengeNil, err
	}
	return category, nil
}

// ChallengeFromUint8 returns the Challenge enum based on a given uint8 value
//
// Parameters:
//
// value: The uint8 value to search on Challenges
//
// Returns:
//
// The Challenge enum value, or an error if the key wasn't found for the given value
func ChallengeFromUint8(value uint8) (Challenge, error) {
	category, ok := Challenges[value]
	if !ok {
		return ChallengeNil, fmt.Errorf(ErrInvalidChallengeUint8, value)
	}
	return category, nil
}