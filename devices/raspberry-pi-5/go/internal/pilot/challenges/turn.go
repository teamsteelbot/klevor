package challenges

import (
	"context"
	"fmt"
	"math"
	"time"

	goconcurrentlogger "github.com/ralvarezdev/go-concurrent-logger"
	gorplidarsdkhandler "github.com/ralvarezdev/go-rplidar-sdk-handler"
)

// turnHandler handles the turning logic based on BNO08x sensor data.
//
// Parameters:
//
// ctx: The context to use for the challenge
// service: The service to use for the challenge
// last90DegreeTurns: A pointer to the last recorded number of 90-degree turns
// isTurning: A pointer to a boolean indicating if the robot is currently turning
// lastTurningTime: A pointer to the last time the robot started turning
// direction: A pointer to the current servo direction
// handlerLoggerProducer: The logger producer to use for logging
//
// Returns:
//
// A boolean indicating if a turn was handled, and an error if the turn could not be handled, nil otherwise
func turnHandler(
	ctx context.Context,
	service Service,
	last90DegreeTurns *uint,
	isTurning *bool,
	lastTurningTime *time.Time,
	direction *ServoDirection,
	handlerLoggerProducer goconcurrentlogger.LoggerProducer,
) (bool, error) {
	// Check if the service is nil
	if service == nil {
		return false, ErrNilService
	}

	// Check if the last90DegreeTurns is nil
	if last90DegreeTurns == nil {
		return false, ErrNilLast90DegreeTurns
	}

	// Check if the isTurning is nil
	if isTurning == nil {
		return false, ErrNilIsTurning
	}

	// Check if the lastTurningTime is nil
	if lastTurningTime == nil {
		return false, ErrNilLastTurningTime
	}

	// Check if the direction is nil
	if direction == nil {
		return false, ErrNilDirection
	}

	// Omit if it's not turning
	if !*isTurning {
		return false, nil
	}

	// Get the latest BNO08x turns value
	turns := service.Get90DegreeTurns()

	// Check if the turns have increased
	if turns > *last90DegreeTurns {
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

		// Update the last turns value
		*last90DegreeTurns = turns

		return true, nil
	}
	return false, nil
}

// detectTurnHandler is the handler for detecting turns using the BNO08x sensor
//
// Parameters:
//
// ctx: The context to use for the challenge
// service: The service to use for the challenge
// last90DegreeTurns: The last recorded number of 90-degree turns
// isTurning: A pointer to a boolean indicating if the robot is currently turning
// lastTurningTime: The last time the robot started turning
// direction: A pointer to the current servo direction
//
// Returns:
//
// An error if the turn could not be detected, nil otherwise
func detectTurnHandler(
	ctx context.Context,
	service Service,
	last90DegreeTurns *uint,
	isTurning *bool,
	lastTurningTime *time.Time,
	direction *ServoDirection,
) error {
	// Check if the service is nil
	if service == nil {
		return ErrNilService
	}

	// Check if the last90DegreeTurns is nil
	if last90DegreeTurns == nil {
		return ErrNilLast90DegreeTurns
	}

	// Check if the isTurning is nil
	if isTurning == nil {
		return ErrNilIsTurning
	}

	// Check if the lastTurningTime is nil
	if lastTurningTime == nil {
		return ErrNilLastTurningTime
	}

	// Check if the direction is nil
	if direction == nil {
		return ErrNilDirection
	}

	// If it's already turning, do nothing
	if *isTurning {
		return nil
	}

	// Get the front distance change
	northAverageDistance := service.GetNorthAverageDistance()
	northDistanceChange := FrontDistanceChange * service.GetRPLiDARAverageDistanceChange(gorplidarsdkhandler.CardinalDirectionNorth)

	// Get the west and east average distances
	westAverageDistance := service.GetWestAverageDistance()
	eastAverageDistance := service.GetEastAverageDistance()

	// Check if the robot should turn left or right based on the side distances
	if *last90DegreeTurns == 0 ||
		(!math.IsNaN(northAverageDistance) &&
			northAverageDistance < northDistanceChange &&
			northAverageDistance+northDistanceChange <= FrontStartTurnDistanceThreshold) {
		if time.Since(*lastTurningTime) >= MinTimeBetweenTurns {
			if (*direction == ServoDirectionRight || *direction == ServoDirectionNil) &&
				(!math.IsNaN(eastAverageDistance) && eastAverageDistance >= SideDistanceThreshold) {
				*isTurning = true

				// Set the direction if it's nil
				if *direction == ServoDirectionNil {
					*direction = ServoDirectionRight
				}
			} else if (*direction == ServoDirectionLeft || *direction == ServoDirectionNil) &&
				(!math.IsNaN(westAverageDistance) && westAverageDistance >= SideDistanceThreshold) {
				*isTurning = true

				// Set the direction if it's nil
				if *direction == ServoDirectionNil {
					*direction = ServoDirectionLeft
				}
			}
			if *isTurning {
				if err := service.SetServoAngle(
					ctx,
					ServoBigTurnAnglePercentage,
					*direction,
				); err != nil {
					return err
				}
			}
		}

		// Move forward at turning speed
		if err := service.SetMotorForward(
			ctx,
			MotorTurningPercentage,
		); err != nil {
			return err
		}
		return nil
	}
	return nil
}
