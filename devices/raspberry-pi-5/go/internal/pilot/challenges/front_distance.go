package challenges

import (
	"context"
	"fmt"
	"math"
	"time"

	goconcurrentlogger "github.com/ralvarezdev/go-concurrent-logger"
	gorplidarsdkhandler "github.com/ralvarezdev/go-rplidar-sdk-handler"
)

// safetyFrontDistanceHandler handles the safety front distance
//
// Parameters:
//
// ctx: The context to use for the challenge
// service: The service to use for the challenge
// isTurning: A flag indicating if the robot is currently turning
// cardinalDirections: The cardinal directions to check the front distances (e.g., North, North-Northeast, North-Northwest)
//
// Returns:
//
// A boolean indicating if the safety front distance was handled, and an error if the safety front distance could not be handled, nil otherwise
func safetyFrontDistanceHandler(
	ctx context.Context,
	service Service,
	handlerLoggerProducer goconcurrentlogger.LoggerProducer,
	isTurning bool,
	cardinalDirections ...gorplidarsdkhandler.CardinalDirection,
) (bool, error) {
	// Check if the service is nil
	if service == nil {
		return false, ErrNilService
	}

	// Check if the cardinal directions are nil
	if len(cardinalDirections) == 0 {
		return false, ErrNoCardinalDirections
	}

	// Check if any of the front distances is below the safety threshold
	cardinalDirectionTrigger := gorplidarsdkhandler.CardinalDirectionNil
	for _, cardinalDirection := range cardinalDirections {
		// Get the average distance for the cardinal direction
		distance := service.GetRPLiDARAverageDistance(cardinalDirection)

		// Calculate the future distance change based on the current distance change
		distanceChange := FrontDistanceChange * service.GetRPLiDARAverageDistanceChange(cardinalDirection)

		// If the distance is above or equal to the threshold, continue to the next direction
		if math.IsNaN(distance) || distance+distanceChange >= SafetyFrontDistanceStartThreshold {
			continue
		}

		// Set the flag to true
		cardinalDirectionTrigger = cardinalDirection
		break
	}
	if cardinalDirectionTrigger == gorplidarsdkhandler.CardinalDirectionNil {
		return false, nil
	}

	// Save previous servo angle, direction and motor speed
	previousServoAngle := service.GetServoAngle()
	previousServoDirection := service.GetServoDirection()
	previousMotorSpeed := service.GetMotorSpeed()

	// Log the warning
	if handlerLoggerProducer != nil {
		handlerLoggerProducer.Warning(
			fmt.Sprintf(
				"Cardinal direction %s front distance is below the safety threshold %f: %f",
				cardinalDirectionTrigger.String(),
				SafetyFrontDistanceStartThreshold,
				service.GetRPLiDARAverageDistance(cardinalDirectionTrigger),
			),
		)
	}

	// Set the servo to center and the motor to backward
	if err := service.SetServoToCenter(ctx); err != nil {
		return true, err
	}

	if err := service.SetMotorBackward(
		ctx,
		MotorBackwardFastPercentage,
	); err != nil {
		return true, err
	}

	var safe bool
	for !safe {
		time.Sleep(UpdateDelay)

		select {
		case <-ctx.Done():
			return true, ctx.Err()
		default:
			// Check if the front distance threshold to stop backward movement is reached
			frontDistanceThresholdReached := true
			for _, cardinalDirection := range cardinalDirections {
				// Get the average distance for the cardinal direction
				distance := service.GetRPLiDARAverageDistance(cardinalDirection)

				// Calculate the future distance change based on the current distance change
				distanceChange := FrontDistanceChange * service.GetRPLiDARAverageDistanceChange(cardinalDirection)

				// If the distance is below the stop threshold, set the flag to false and break the loop
				if !math.IsNaN(distance) && distance+distanceChange < SafetyFrontDistanceStopThreshold {
					frontDistanceThresholdReached = false
					break
				}
			}

			if frontDistanceThresholdReached {
				if handlerLoggerProducer != nil {
					handlerLoggerProducer.Info("Safety front distance threshold reached.")
				}
				safe = true
			}
		}
	}

	// Set previous servo angle and motor speed back to normal
	if isTurning {
		if err := service.SetServoAngle(
			ctx,
			previousServoAngle,
			previousServoDirection,
		); err != nil {
			return true, err
		}
	} else if err := service.SetServoToOppositeDirection(
		ctx,
		previousServoAngle,
	); err != nil {
		return true, err
	}
	if err := service.SetMotorSpeed(
		ctx,
		previousMotorSpeed,
		MotorDirectionForward,
	); err != nil {
		return true, err
	}
	return true, nil
}
