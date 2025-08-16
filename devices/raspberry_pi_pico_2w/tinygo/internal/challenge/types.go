package challenge

import (
	challengeenums "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/challenge/enums"
	"github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/pulldown"
)

type (
	// DefaultHandler is the default implementation of the Handler interface.
	DefaultHandler struct {
		obstaclesPullDownHandler pulldown.Handler
		parkingPullDownHandler   pulldown.Handler
	}
)

// NewDefaultHandler creates a new instance of DefaultHandler
//
// Parameters:
//
// pullDownHandler: The pull-down handler to use
//
// Returns:
//
// An instance of DefaultHandler, or an error if the pull-down handler is nil
func NewDefaultHandler(
	obstaclesPullDownHandler pulldown.Handler,
	parkingPullDownHandler pulldown.Handler,
) (*DefaultHandler, error) {
	if obstaclesPullDownHandler == nil {
		return nil, ErrNilObstaclesPullDownHandler
	}
	if parkingPullDownHandler == nil {
		return nil, ErrNilParkingPullDownHandler
	}

	return &DefaultHandler{
		obstaclesPullDownHandler,
		parkingPullDownHandler,
	}, nil
}

// IsWithObstacles checks if the challenge is with obstacles but not parking.
//
// Returns:
//
// True if the pull-down for obstacles is shorted and the pull-down for parking is open, false otherwise.
func (d *DefaultHandler) IsWithObstacles() bool {
	return d.obstaclesPullDownHandler.IsShorted() && d.parkingPullDownHandler.IsOpen()
}

// IsWithObstaclesAndParking checks if the challenge is with obstacles and parking.
//
// Returns:
//
// True if both pull-downs for obstacles and parking are shorted, false otherwise.
func (d *DefaultHandler) IsWithObstaclesAndParking() bool {
	return d.obstaclesPullDownHandler.IsShorted() && d.parkingPullDownHandler.IsShorted()
}

// IsWithoutObstacles checks if the challenge is without obstacles.
//
// Returns:
//
// True if the pull-down for obstacles is open, false otherwise.
func (d *DefaultHandler) IsWithoutObstacles() bool {
	return d.obstaclesPullDownHandler.IsOpen()
}

// GetChallenge returns the current challenge based on the pull-down states.
//
// Returns:
//
// The current challenge as an enum value.
func (d *DefaultHandler) GetChallenge() challengeenums.Challenge {
	if d.IsWithObstaclesAndParking() {
		return challengeenums.ChallengeWithObstaclesAndParking
	} else if d.IsWithObstacles() {
		return challengeenums.ChallengeWithObstacles
	} else if d.IsWithoutObstacles() {
		return challengeenums.ChallengeWithoutObstacles
	}
	return challengeenums.ChallengeNil
}
