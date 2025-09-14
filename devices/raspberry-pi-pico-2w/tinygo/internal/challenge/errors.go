package challenge

import (
	tinygotypes "github.com/ralvarezdev/tinygo-types"
)

const (
	// ErrorCodeChallengeStartNumber is the starting number for challenge-related error codes.
	ErrorCodeChallengeStartNumber uint16 = 1
)

const (
	ErrorCodeChallengeNilHandler tinygotypes.ErrorCode = tinygotypes.ErrorCode(iota + ErrorCodeChallengeStartNumber)
	ErrorCodeChallengeNilObstaclesPullUpHandler
	ErrorCodeChallengeNilParkingPullUpHandler
	ErrorCodeChallengeInvalidChallengeUint8
)
