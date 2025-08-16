package enums

import (
	"fmt"
	"strings"
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
)

// String returns the string representation of the Challenge
//
// Returns:
//
// The string representation of the Challenge enum
func (c Challenge) String() string {
	return ChallengeNames[c]
}

// ChallengeFromString returns the Challenge enum based on a given string
//
// Parameters:
//
// s: The string name to search on ChallengeNames
//
// Returns:
//
// The Challenge enum value, or an error if the key wasn't found for the given value
func ChallengeFromString(s string) (Challenge, error) {
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
