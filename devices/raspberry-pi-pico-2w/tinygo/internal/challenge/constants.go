package challenge

import (
	"fmt"

	"machine"

	internalpullup "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/pullup"
)

var (
	// ObstaclesPullUpHandler is the handler for the pull-up to enable/disable obstacles.
	ObstaclesPullUpHandler internalpullup.Handler = internalpullup.NewDefaultHandler(machine.GPIO21)

	// ParkingPullUpHandler is the handler for the pull-up to enable/disable parking.
	ParkingPullUpHandler internalpullup.Handler = internalpullup.NewDefaultHandler(machine.GPIO17)

	// ChallengeHandler is the default challenge handler that uses the pull-up handler.
	ChallengeHandler Handler
)

func init() {
	// Call the setup functions to initialize the pull-ups
	ObstaclesPullUpHandler.Setup()
	ParkingPullUpHandler.Setup()

	// ChallengeHandler is the default challenge handler that uses the pull-up handler.
	challengeHandler, err := NewDefaultHandler(
		ObstaclesPullUpHandler,
		ParkingPullUpHandler,
	)
	if err != nil {
		panic(fmt.Errorf("failed to initialize challenge: %w", err))
	}
	ChallengeHandler = challengeHandler
}
