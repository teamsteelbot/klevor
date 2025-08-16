package challenge

import (
	challengeenums "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/challenge/enums"
)

type (
	// Handler is the interface to manage the challenge state.
	Handler interface {
		IsWithObstacles() bool
		IsWithoutObstacles() bool
		IsWithObstaclesAndParking() bool
		GetChallenge() challengeenums.Challenge
	}
)
