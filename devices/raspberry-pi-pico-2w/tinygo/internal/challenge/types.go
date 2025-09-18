package challenge

import (
	tinygoerrors "github.com/ralvarezdev/tinygo-errors"
	tinygopullup "github.com/ralvarezdev/tinygo-pullup"
)

type (
	// DefaultHandler is the default implementation of the Handler interface.
	DefaultHandler struct {
		obstaclesPullUpHandler tinygopullup.Handler
		parkingPullUpHandler   tinygopullup.Handler
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
	obstaclesPullUpHandler tinygopullup.Handler,
	parkingPullUpHandler tinygopullup.Handler,
) (*DefaultHandler, tinygoerrors.ErrorCode) {
	// Check if one of the pull-up handlers is nil
	if obstaclesPullUpHandler == nil {
		return nil, ErrorCodeChallengeNilObstaclesPullUpHandler
	}
	if parkingPullUpHandler == nil {
		return nil, ErrorCodeChallengeNilParkingPullUpHandler
	}

	return &DefaultHandler{
		obstaclesPullUpHandler,
		parkingPullUpHandler,
	}, tinygoerrors.ErrorCodeNil
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
func (d *DefaultHandler) GetChallenge() Challenge {
	if d.IsWithObstaclesAndParking() {
		return ChallengeWithObstaclesAndParking
	} else if d.IsWithObstacles() {
		return ChallengeWithObstacles
	} else if d.IsWithoutObstacles() {
		return ChallengeWithoutObstacles
	}
	return ChallengeNil
}
