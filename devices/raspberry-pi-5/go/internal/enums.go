package internal

import (
	"fmt"
)

type (
	// Challenge represents the enum challenge messages sent and received from the Raspberry Pi Pico
	Challenge uint8
)

const (
	ChallengeNil Challenge = iota
	ChallengeWithoutObstacles
	ChallengeWithObstacles
	ChallengeWithObstaclesAndParking
)

var (
	// ChallengeNames maps a given Challenge to its string name
	ChallengeNames = map[Challenge]string{
		ChallengeWithObstacles:           "with_obstacles",
		ChallengeWithoutObstacles:        "without_obstacles",
		ChallengeWithObstaclesAndParking: "with_obstacles_and_parking",
	}

	// Challenges maps a given uint8 value to its Challenge enum
	Challenges = map[uint8]Challenge{
		uint8(ChallengeNil):                 ChallengeNil,
		uint8(ChallengeWithObstacles):       ChallengeWithObstacles,
		uint8(ChallengeWithoutObstacles):    ChallengeWithoutObstacles,
		uint8(ChallengeWithObstaclesAndParking): ChallengeWithObstaclesAndParking,
	}
)

// String returns the name of the Challenge
//
// Returns:
//
// The name of the Challenge enum
func (c Challenge) String() string {
	return ChallengeNames[c]
}

// Bytes returns the byte slice representation of the Challenge
//
// Returns:
//
// The byte slice representation of the Challenge enum
func (c Challenge) Bytes() []byte {
	return []byte{uint8(c)}
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
		return ChallengeNil, fmt.Errorf(ErrUnknownChallenge, value)
	}
	return category, nil
}

// ChallengeFromBytes returns the Challenge enum based on a given byte slice
//
// Parameters:
//
// data: The byte slice to parse as Challenge
//
// Returns:
//
// The Challenge enum value, or an error if the key wasn't found for the given value
func ChallengeFromBytes(data []byte) (Challenge, error) {
	if len(data) == 0 {
		return ChallengeNil, ErrNilChallenge 
	}
	return ChallengeFromUint8(data[0])
}