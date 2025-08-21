package challenge

import (
	internalchallengeenums "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/challenge/enums"
	internalpullup "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/pullup"
)

type (
	// DefaultHandler is the default implementation of the Handler interface.
	DefaultHandler struct {
		obstaclesPullUpHandler internalpullup.Handler
		parkingPullUpHandler   internalpullup.Handler
	}
)

// NewDefaultHandler creates a new instance of DefaultHandler
//
// Parameters:
//
// pullUpHandler: The pull-up handler to use
//
// Returns:
//
// An instance of DefaultHandler, or an error if the pull-up handler is nil
func NewDefaultHandler(
	obstaclesPullUpHandler internalpullup.Handler,
	parkingPullUpHandler internalpullup.Handler,
) (*DefaultHandler, error) {
	if obstaclesPullUpHandler == nil {
		return nil, ErrNilObstaclesPullUpHandler
	}
	if parkingPullUpHandler == nil {
		return nil, ErrNilParkingPullUpHandler
	}

	return &DefaultHandler{
		obstaclesPullUpHandler,
		parkingPullUpHandler,
	}, nil
}

// IsWithObstacles checks if the challenge is with obstacles but not parking.
//
// Returns:
//
// True if the pull-up for obstacles is shorted and the pull-up for parking is open, false otherwise.
func (d *DefaultHandler) IsWithObstacles() bool {
	return d.obstaclesPullUpHandler.IsShorted() && d.parkingPullUpHandler.IsOpen()
}

// IsWithObstaclesAndParking checks if the challenge is with obstacles and parking.
//
// Returns:
//
// True if both pull-ups for obstacles and parking are shorted, false otherwise.
func (d *DefaultHandler) IsWithObstaclesAndParking() bool {
	return d.obstaclesPullUpHandler.IsShorted() && d.parkingPullUpHandler.IsShorted()
}

// IsWithoutObstacles checks if the challenge is without obstacles.
//
// Returns:
//
// True if the pull-up for obstacles is open, false otherwise.
func (d *DefaultHandler) IsWithoutObstacles() bool {
	return d.obstaclesPullUpHandler.IsOpen()
}

// GetChallenge returns the current challenge based on the pull-up states.
//
// Returns:
//
// The current challenge as an enum value.
func (d *DefaultHandler) GetChallenge() internalchallengeenums.Challenge {
	if d.IsWithObstaclesAndParking() {
		return internalchallengeenums.ChallengeWithObstaclesAndParking
	} else if d.IsWithObstacles() {
		return internalchallengeenums.ChallengeWithObstacles
	} else if d.IsWithoutObstacles() {
		return internalchallengeenums.ChallengeWithoutObstacles
	}
	return internalchallengeenums.ChallengeNil
}
