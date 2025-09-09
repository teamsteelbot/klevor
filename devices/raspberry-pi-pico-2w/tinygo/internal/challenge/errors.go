package challenge

import (
	tinygotypes "github.com/ralvarezdev/tinygo-types"
	"github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal"
)

const (
	ErrorCodeChallengeNilHandler tinygotypes.ErrorCode = tinygotypes.ErrorCode(iota + internal.ErrorCodeChallengeStartNumber)
	ErrorCodeChallengeNilObstaclesPullUpHandler
	ErrorCodeChallengeNilParkingPullUpHandler
	ErrorCodeChallengeInvalidChallengeUint8
)
