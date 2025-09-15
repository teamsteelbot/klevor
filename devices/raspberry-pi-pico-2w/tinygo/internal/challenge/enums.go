package challenge

import (
	tinygoerrors "github.com/ralvarezdev/tinygo-errors"
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
func ChallengeFromUint8(value uint8) (Challenge, tinygoerrors.ErrorCode) {
	switch Challenge(value) {
	case ChallengeNil:
		return ChallengeNil, tinygoerrors.ErrorCodeNil
	case ChallengeWithObstacles:
		return ChallengeWithObstacles, tinygoerrors.ErrorCodeNil
	case ChallengeWithoutObstacles:
		return ChallengeWithoutObstacles, tinygoerrors.ErrorCodeNil
	case ChallengeWithObstaclesAndParking:
		return ChallengeWithObstaclesAndParking, tinygoerrors.ErrorCodeNil
	default:
		return ChallengeNil, ErrorCodeChallengeInvalidChallengeUint8
	}
}
