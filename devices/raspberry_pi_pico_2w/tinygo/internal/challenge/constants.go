package challenge

import (
	"machine"

	internalpullup "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/pullup"
)

var (
	// ObstaclesPullUpHandler is the handler for the pull-up to enable/disable obstacles.
	ObstaclesPullUpHandler internalpullup.Handler = internalpullup.NewDefaultHandler(machine.GPIO21)

	// ParkingPullUpHandler is the handler for the pull-up to enable/disable parking.
	ParkingPullUpHandler internalpullup.Handler = internalpullup.NewDefaultHandler(machine.GPIO17)

	// ChallengeHandler is the default challenge handler that uses the pull-up handler.
	ChallengeHandler, _ = NewDefaultHandler(
		ObstaclesPullUpHandler,
		ParkingPullUpHandler,
	)
)

func init() {
	// Call the setup functions to initialize the pull-ups
	ObstaclesPullUpHandler.Setup()
	ParkingPullUpHandler.Setup()
}
