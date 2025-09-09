package challenge

import (
	tinygotypes "github.com/ralvarezdev/tinygo-types"
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

// ChallengeFromUint8 returns the Challenge enum based on a given uint8 value
//
// Parameters:
//
// value: The uint8 value to search on Challenges
//
// Returns:
//
// The Challenge enum value, or an error if the key wasn't found for the given value
func ChallengeFromUint8(value uint8) (Challenge, tinygotypes.ErrorCode) {
	switch Challenge(value) {
	case ChallengeNil:
		return ChallengeNil, tinygotypes.ErrorCodeNil
	case ChallengeWithObstacles:
		return ChallengeWithObstacles, tinygotypes.ErrorCodeNil
	case ChallengeWithoutObstacles:
		return ChallengeWithoutObstacles, tinygotypes.ErrorCodeNil
	case ChallengeWithObstaclesAndParking:
		return ChallengeWithObstaclesAndParking, tinygotypes.ErrorCodeNil
	default:
		return ChallengeNil, ErrorCodeChallengeInvalidChallengeUint8
	}
}
