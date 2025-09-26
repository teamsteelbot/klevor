package challenges

import (
	"context"
	"fmt"
	"math"
	"time"

	goconcurrentlogger "github.com/ralvarezdev/go-concurrent-logger"
	gorplidarsdkhandler "github.com/ralvarezdev/go-rplidar-sdk-handler"
)

const (
	// MinBackwardTime is the minimum time to move backward when a collision is detected
	MinBackwardTime = 100 * time.Millisecond
)

// collisionHandler handles the collision logic based on RPLiDAR sensor data.
//
// Parameters:
//
// ctx: The context to use for the challenge
// service: The service to use for the challenge
// isTurning: A flag indicating if the robot is currently turning
// loggerProducer: The logger producer to use for logging
// cardinalDirections: The cardinal directions to check the front distances (e.g., North, North-Northeast, North-Northwest)
//
// Returns:
//
// A boolean indicating if a collision was detected and handled, and an error if the collision could not be handled, nil otherwise
func collisionHandler(
	ctx context.Context,
	service Service,
	isTurning bool,
	loggerProducer goconcurrentlogger.LoggerProducer,
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
		// Calculate the future distance based on the current distance change
		distance := service.GetRPLiDARAverageDistanceOnNextUpdate(
			cardinalDirection,
		)

		// Check if the distance is NaN (no data)
		if math.IsNaN(distance) {
			continue
		}

		// Get the appropriate safety front distance start threshold based on the cardinal direction
		frontDistanceStartThreshold := getFrontStartDistanceThresholdFromCardinalDirection(cardinalDirection)

		// If the distance is above or equal to the threshold, continue to the next direction
		if distance >= frontDistanceStartThreshold {
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
	previousMotorDirection := service.GetMotorDirection()

	// Log the warning
	if loggerProducer != nil {
		loggerProducer.Warning(
			fmt.Sprintf(
				"Cardinal direction %s front distance is below the safety threshold %f, current: %f, calculated next update: %f",
				cardinalDirectionTrigger.String(),
				getFrontStartDistanceThresholdFromCardinalDirection(cardinalDirectionTrigger),
				service.GetRPLiDARAverageDistance(cardinalDirectionTrigger),
				service.GetRPLiDARAverageDistanceOnNextUpdate(cardinalDirectionTrigger),
			),
		)
	}

	// Stop the motor to prevent further movement
	if previousMotorDirection != MotorDirectionStop {
		if err := service.SetMotorStop(ctx); err != nil {
			return true, err
		}
	}

	// Check if the robot is turning (new strategy)
	if isTurning {
		// If the robot is not turning, set the servo to the opposite direction
		if err := service.SetServoToOppositeDirection(
			ctx,
			previousServoAngle,
		); err != nil {
			return true, err
		}
	} else {
		// If the robot is turning, set the servo to center
		if err := service.SetServoToCenter(ctx); err != nil {
			return true, err
		}
	}

	/*
		// Set the servo to center
		if err := service.SetServoToCenter(ctx); err != nil {
			return true, err
		}
	*/

	// Move backward at fast speed
	if err := service.SetMotorBackward(
		ctx,
		MotorBackwardNormalSpeed,
	); err != nil {
		return true, err
	}

	// Log that the robot is moving backward
	if loggerProducer != nil {
		loggerProducer.Info("Moving backward...")
	}

	// If it's turning, we don't care about the front distance, only the back distance
	if isTurning {
		if err := backCloseUpHandler(
			ctx,
			service,
			loggerProducer,
		); err != nil {
			return true, err
		}
	} else {
		// Wait until the front distance is above the stop threshold or an obstacle is detected on the back
		if err := safeFrontHandler(
			ctx,
			service,
			loggerProducer,
			cardinalDirections...,
		); err != nil {
			return true, err
		}
	}

	// Stop the motor after reaching a safe distance
	if err := service.SetMotorStop(ctx); err != nil {
		return true, err
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
	if previousMotorDirection != MotorDirectionStop {
		if err := service.SetMotorSpeed(
			ctx,
			previousMotorSpeed,
			MotorDirectionForward,
		); err != nil {
			return true, err
		}
	}
	return true, nil
}

// backCloseUpHandler handles the back close up logic based on RPLiDAR sensor data.
//
// Parameters:
//
// ctx: The context to use for the challenge
// service: The service to use for the challenge
// loggerProducer: The logger producer to use for logging
//
// Returns:
//
// An error if the back close up could not be handled, nil otherwise
func backCloseUpHandler(
	ctx context.Context,
	service Service,
	loggerProducer goconcurrentlogger.LoggerProducer,
) error {
	// Check if the service is nil
	if service == nil {
		return ErrNilService
	}

	// Check if it's going backward
	if service.GetMotorDirection() != MotorDirectionBackward {
		return fmt.Errorf("back close up handler can only be used when going backward")
	}

	// Wait for the minimum backward time to ensure the robot moves backward a bit
	time.Sleep(MinBackwardTime)

	// Wait until the back distance is above the threshold
	for {
		time.Sleep(UpdateDelay)

		select {
		case <-ctx.Done():
			return ctx.Err()
		default:
			// Check if there's any obstacle on the back
			for _, cardinalDirection := range BackCardinalDirections {
				// Calculate the future distance based on the current distance change
				distance := service.GetRPLiDARAverageDistanceOnNextUpdate(
					cardinalDirection,
				)

				// Check if the distance is NaN (no data)
				if math.IsNaN(distance) {
					continue
				}

				// Get the appropriate back distance threshold based on the cardinal direction
				backStopDistanceThreshold := getBackStopDistanceThresholdFromCardinalDirection(cardinalDirection)

				// If the distance is below the back threshold, set the flag to false and break the loop
				if distance < backStopDistanceThreshold {
					if loggerProducer != nil {
						loggerProducer.Warning("Safety back distance threshold reached. Stopping backward movement.")
					}
					return nil
				}
			}
		}
	}
}

// safeFrontHandler handles the safe front logic based on RPLiDAR sensor data.
//
// Parameters:
//
// ctx: The context to use for the challenge
// service: The service to use for the challenge
// loggerProducer: The logger producer to use for logging
// cardinalDirections: The cardinal directions to check the front distances (e.g., North, North-Northeast, North-Northwest)
//
// Returns:
//
// An error if the safe front could not be handled, nil otherwise
func safeFrontHandler(
	ctx context.Context,
	service Service,
	loggerProducer goconcurrentlogger.LoggerProducer,
	cardinalDirections ...gorplidarsdkhandler.CardinalDirection,
) error {
	// Check if the service is nil
	if service == nil {
		return ErrNilService
	}

	// Check if it's going backward
	if service.GetMotorDirection() != MotorDirectionBackward {
		return fmt.Errorf("safe front handler can only be used when going backward")
	}

	// Sleep for the minimum backward time to ensure the robot moves backward a bit
	time.Sleep(MinBackwardTime)

	// Wait until the front distance is above the stop threshold or an obstacle is detected on the back
	for {
		time.Sleep(UpdateDelay)

		select {
		case <-ctx.Done():
			return ctx.Err()
		default:
			// Check if there's any obstacle on the back
			backDistanceThresholdReached := false
			for _, cardinalDirection := range BackCardinalDirections {
				// Calculate the future distance change based on the current distance change
				distance := service.GetRPLiDARAverageDistanceOnNextUpdate(
					cardinalDirection,
				)

				// Check if the distance is NaN (no data)
				if math.IsNaN(distance) {
					continue
				}

				// Get the appropriate back distance threshold based on the cardinal direction
				backStopDistanceThreshold := getBackStopDistanceThresholdFromCardinalDirection(cardinalDirection)

				// If the distance is below the back threshold, set the flag to false and break the loop
				if distance < backStopDistanceThreshold {

					backDistanceThresholdReached = true
					break
				}
			}

			// Check if the back distance threshold to stop backward movement is reached
			if backDistanceThresholdReached {
				if loggerProducer != nil {
					loggerProducer.Warning("Safety back distance threshold reached. Stopping backward movement.")
				}
				return nil
			}

			// Check if the front distance threshold to stop backward movement is reached
			frontDistanceThresholdReached := true
			for _, cardinalDirection := range cardinalDirections {
				// Calculate the future distance change based on the current distance change
				distance := service.GetRPLiDARAverageDistanceOnNextUpdate(
					cardinalDirection,
				)

				// Check if the distance is NaN (no data)
				if math.IsNaN(distance) {
					continue
				}

				// Get the appropriate safety front distance stop threshold based on the cardinal direction
				safetyFrontDistanceStopThreshold := getFrontStartDistanceThresholdFromCardinalDirection(cardinalDirection)

				// If the distance is below the stop threshold, set the flag to false and break the loop
				if distance < safetyFrontDistanceStopThreshold {
					frontDistanceThresholdReached = false
					break
				}
			}

			// If the front distance threshold is reached, set the reached flag to true
			if frontDistanceThresholdReached {
				if loggerProducer != nil {
					loggerProducer.Info("Safety front distance threshold reached. Resuming normal operation.")
				}
				return nil
			}
		}
	}
}
