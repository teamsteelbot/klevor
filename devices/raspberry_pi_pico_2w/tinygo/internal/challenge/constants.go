package challenge

import (
	"machine"

	"github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/pulldown"
)

var (
	// ObstaclesPullDownHandler is the handler for the pull-down to enable/disable obstacles.
	ObstaclesPullDownHandler pulldown.Handler = pulldown.NewDefaultHandler(machine.GPIO21)

	// ParkingPullDownHandler is the handler for the pull-down to enable/disable parking.
	ParkingPullDownHandler pulldown.Handler = pulldown.NewDefaultHandler(machine.GPIO17)

	// ChallengeHandler is the default challenge handler that uses the pull-down handler.
	ChallengeHandler, _ = NewDefaultHandler(
		ObstaclesPullDownHandler,
		ParkingPullDownHandler,
	)
)
