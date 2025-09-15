package challenge

import (
	tinygoerrors "github.com/ralvarezdev/tinygo-errors"
)

const (
	// ErrorCodeChallengeStartNumber is the starting number for challenge-related error codes.
	ErrorCodeChallengeStartNumber uint16 = 1
)

const (
	ErrorCodeChallengeNilHandler tinygoerrors.ErrorCode = tinygoerrors.ErrorCode(iota + ErrorCodeChallengeStartNumber)
	ErrorCodeChallengeNilObstaclesPullUpHandler
	ErrorCodeChallengeNilParkingPullUpHandler
	ErrorCodeChallengeInvalidChallengeUint8
)
