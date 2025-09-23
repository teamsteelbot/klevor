package challenges

import (
	"context"
	"fmt"

	goconcurrentlogger "github.com/ralvarezdev/go-concurrent-logger"
)

// turnHandler handles the turning logic based on BNO08x sensor data.
//
// Parameters:
//
// ctx: The context to use for the challenge
// service: The service to use for the challenge
// last90DegreeTurns: The last recorded number of 90-degree turns
// handlerLoggerProducer: The logger producer to use for logging
//
// Returns:
//
// A boolean indicating if a turn was handled, and an error if the turn could not be handled, nil otherwise
func turnHandler(
	ctx context.Context,
	service Service,
	last90DegreeTurns uint,
	handlerLoggerProducer goconcurrentlogger.LoggerProducer,
) (bool, error) {
	// Check if the service is nil
	if service == nil {
		return false, ErrNilService
	}

	// Get the latest BNO08x turns value
	turns := service.Get90DegreeTurns()

	// Check if the turns have increased
	if turns > last90DegreeTurns {
		handlerLoggerProducer.Info(
			fmt.Sprintf(
				"Detected a 90-degree turn. Current turns: %d, Last turns: %d",
				turns,
				last90DegreeTurns,
			),
		)

		// Set the servo to center
		if err := service.SetServoToCenter(ctx); err != nil {
			return true, err
		}
		return true, nil
	}
	return false, nil
}
