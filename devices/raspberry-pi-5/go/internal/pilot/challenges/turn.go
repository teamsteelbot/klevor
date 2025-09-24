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
	// SideDistanceThreshold is the distance threshold for side sensors
	SideDistanceThreshold = 1500.0

	// FrontStartTurnDistanceThreshold is the distance threshold to start turning
	FrontStartTurnDistanceThreshold = 1000.0 // 500.0, 600.0, 650.0, 900.0

	// SafetyFrontDistanceStartTurnThreshold is the distance threshold to start turning
	SafetyFrontDistanceStartTurnThreshold = 700.0 // 600.0

	// LaneIdentifierThreshold is used to determine which lane is the robot placed (only used in the closed challenge)
	LaneIdentifierThreshold = 400.0

	// FrontCloseupThreshold is used to move the robot closely to the wall (only used in the closed challenge)
	FrontCloseupThreshold = 100.0

	// MinTimeBetweenTurns is the minimum time between turns
	MinTimeBetweenTurns = 2 * time.Second

	// MinTimeBetweenTurnByWallCloseUp is the minimum time between turns by wall close up
	MinTimeBetweenTurnByWallCloseUp = 3 * time.Second
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
// loggerProducer: The logger producer to use for logging
//
// Returns:
//
// A boolean indicating if a turn was handled, and an error if the turn could not be handled, nil otherwise
func turnHandler(
	ctx context.Context,
	service Service,
	last90DegreeTurns *int,
	isTurning *bool,
	lastTurningTime *time.Time,
	loggerProducer goconcurrentlogger.LoggerProducer,
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

	// Omit if it's not turning
	if !*isTurning {
		return false, nil
	}

	// Get the latest BNO08x turns value
	turns := service.Get90DegreeTurns()

	// Check if the turns have increased
	if turns > *last90DegreeTurns {
		loggerProducer.Info(
			fmt.Sprintf(
				"Detected a 90-degree turn. Current turns: %d, Last turns: %d",
				turns,
				*last90DegreeTurns,
			),
		)

		// Set the servo to center
		if err := service.SetServoToCenter(ctx); err != nil {
			return true, err
		}

		// Update the last turns value
		*last90DegreeTurns = turns

		// Update the last turning time
		*lastTurningTime = time.Now()

		// Reset the turning state
		*isTurning = false

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
// loggerProducer: The logger producer to use for logging
//
// Returns:
//
// An error if the turn could not be detected, nil otherwise
func detectTurnHandler(
	ctx context.Context,
	service Service,
	last90DegreeTurns *int,
	isTurning *bool,
	lastTurningTime *time.Time,
	direction *ServoDirection,
	loggerProducer goconcurrentlogger.LoggerProducer,
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
	northDistance := service.GetNorthAverageDistance()
	northDistanceChange := FrontDistanceChange * service.GetRPLiDARAverageDistanceChange(gorplidarsdkhandler.CardinalDirectionNorth)

	// Check if the front distance and distance change are NaN, if so, return
	if math.IsNaN(northDistance) || math.IsNaN(northDistanceChange) {
		return nil
	}

	// Get the west and east average distances
	westDistance := service.GetWestAverageDistance()
	eastDistance := service.GetEastAverageDistance()

	// Check if the robot should turn left or right based on the side distances
	if *last90DegreeTurns == 0 ||
		northDistance+northDistanceChange <= FrontStartTurnDistanceThreshold {
		if time.Since(*lastTurningTime) >= MinTimeBetweenTurns {
			if (*direction == ServoDirectionRight || *direction == ServoDirectionNil) &&
				(!math.IsNaN(eastDistance) && eastDistance >= SideDistanceThreshold) {
				*isTurning = true

				// Log the turn detection
				if loggerProducer != nil {
					loggerProducer.Info(
						fmt.Sprintf(
							"Detected a turn to the right. Current turns: %d",
							*last90DegreeTurns,
						),
					)
				}

				// Set the direction if it's nil
				*direction = ServoDirectionRight
			} else if (*direction == ServoDirectionLeft || *direction == ServoDirectionNil) &&
				(!math.IsNaN(westDistance) && westDistance >= SideDistanceThreshold) {
				*isTurning = true

				// Log the turn detection
				if loggerProducer != nil {
					loggerProducer.Info(
						fmt.Sprintf(
							"Detected a turn to the left. Current turns: %d",
							*last90DegreeTurns,
						),
					)
				}

				// Set the direction if it's nil
				*direction = ServoDirectionLeft
			}
		}

		// Check if it's turning
		if !*isTurning {
			return nil
		}

		// Check if the front distance is below the turn threshold
		if northDistance+northDistanceChange < SafetyFrontDistanceStartTurnThreshold {
			// Log that the front distance is too close
			if loggerProducer != nil {
				loggerProducer.Info(
					fmt.Sprintf(
						"Front distance (%.2f mm) is below the safety threshold (%.2f mm). Moving backward until it's safe to turn.",
						northDistance+northDistanceChange,
						SafetyFrontDistanceStartTurnThreshold,
					),
				)
			}

			// Go backward if the front distance is below the threshold
			if err := service.SetMotorBackward(
				ctx,
				MotorBackwardNormalSpeed,
			); err != nil {
				return err
			}

			// Wait until the front distance is above the threshold
			reached := false
			for !reached {
				time.Sleep(UpdateDelay)

				select {
				case <-ctx.Done():
					return ctx.Err()
				default:
					// Get the front distance and distance change
					northDistance = service.GetNorthAverageDistance()
					northDistanceChange = FrontDistanceChange * service.GetRPLiDARAverageDistanceChange(gorplidarsdkhandler.CardinalDirectionNorth)

					// Check if any measure is NaN, if so, continue
					if math.IsNaN(northDistance) || math.IsNaN(northDistanceChange) {
						continue
					}

					// If the front distance is above the threshold, stop moving backward
					if northDistance+northDistanceChange >= SafetyFrontDistanceStartTurnThreshold {
						if loggerProducer != nil {
							loggerProducer.Info("Front distance is safe to turn. Resuming turn.")
						}
						if err := service.SetMotorStop(ctx); err != nil {
							return err
						}

						// Set reached flag as true
						reached = true
					}
				}
			}
		}

		// If it's turning, set the servo to the turn angle
		if *isTurning {
			if err := service.SetServoAngle(
				ctx,
				ServoBigTurnAngle,
				*direction,
			); err != nil {
				return err
			}
		}

		// Move forward at turning speed
		if err := service.SetMotorForward(
			ctx,
			MotorTurningSpeed,
		); err != nil {
			return err
		}
		return nil
	}
	return nil
}

// turnByWallCloseUpHandler handles turning where there is a wall close up on the back
//
// Parameters:
//
// ctx: The context to use for the challenge
// service: The service to use for the challenge
// lastTurningTime: A pointer to the last time the robot made a turn
// loggerProducer: The logger producer to use for logging
func turnByWallCloseUpHandler(
	ctx context.Context,
	service Service,
	lastTurningTime *time.Time,
	loggerProducer goconcurrentlogger.LoggerProducer,
) (bool, error) {
	// Check if the service is nil
	if service == nil {
		return false, ErrNilService
	}
	// Check if the lastTurningTime is nil
	if lastTurningTime == nil {
		return false, ErrNilLastTurningTime
	}

	// Check if there isn't enough time has passed since the last turn
	if time.Since(*lastTurningTime) < MinTimeBetweenTurnByWallCloseUp {
		return false, nil
	}

	// Initialize temporary variables
	var (
		shouldTurn          bool
		isTurning           bool
		isTurningCompleted  bool
		wallCloseUp         bool
		isInnerLaneSide     *bool
		toCardinalDirection gorplidarsdkhandler.CardinalDirection
	)

	// Loop until the robot has turned
	for !isTurningCompleted {
		// Sleep for the update delay
		time.Sleep(UpdateDelay)

		select {
		case <-ctx.Done():
			return false, ctx.Err()
		default:
			// Get the average distances from the RPLiDAR
			northDistance := service.GetRPLiDARAverageDistance(gorplidarsdkhandler.CardinalDirectionNorth)
			northDistanceChange := FrontDistanceChange * service.GetRPLiDARAverageDistanceChange(gorplidarsdkhandler.CardinalDirectionNorth)
			eastDistance := service.GetRPLiDARAverageDistance(gorplidarsdkhandler.CardinalDirectionEast)
			eastDistanceChange := SideDistanceChange * service.GetRPLiDARAverageDistanceChange(gorplidarsdkhandler.CardinalDirectionEast)
			westDistance := service.GetRPLiDARAverageDistance(gorplidarsdkhandler.CardinalDirectionWest)
			westDistanceChange := SideDistanceChange * service.GetRPLiDARAverageDistanceChange(gorplidarsdkhandler.CardinalDirectionWest)

			// Get the last recorded number of 90-degree turns
			last90DegreeTurns := service.Get90DegreeTurns()

			// Check if any measure is NaN, if so, continue to the next iteration
			if math.IsNaN(northDistance) || math.IsNaN(northDistanceChange) ||
				math.IsNaN(eastDistance) || math.IsNaN(eastDistanceChange) ||
				math.IsNaN(westDistance) || math.IsNaN(westDistanceChange) {
				continue
			}

			// Check if the robot should turn left or right based on the side distances
			if !shouldTurn && eastDistance+eastDistanceChange >= SideDistanceThreshold {
				shouldTurn = true
			}

			// Check if the robot should turn left or right based on the side distances
			if !shouldTurn && westDistance+westDistanceChange >= SideDistanceThreshold {
				shouldTurn = true
			}

			// If the robot shouldn't be turning, return
			if !shouldTurn {
				return false, nil
			}

			// Check which side has the inner lane (only once)
			if isInnerLaneSide == nil {
				if eastDistance+eastDistanceChange >= SideDistanceThreshold {
					inner := westDistance+westDistanceChange >= LaneIdentifierThreshold
					isInnerLaneSide = &inner
					toCardinalDirection = gorplidarsdkhandler.CardinalDirectionEast
				} else if westDistance+westDistanceChange >= SideDistanceThreshold {
					inner := eastDistance+eastDistanceChange >= LaneIdentifierThreshold
					isInnerLaneSide = &inner
					toCardinalDirection = gorplidarsdkhandler.CardinalDirectionWest
				}
			}

			// Checks which lane is the robot located inside
			switch toCardinalDirection {
			case gorplidarsdkhandler.CardinalDirectionEast:
				// Handle it based on the inner lane side
				switch *isInnerLaneSide {
				case false:
					// Handle a normal turn
					if !isTurning {
						if err := service.SetServoToRight(
							ctx,
							ServoBigTurnAngle,
						); err != nil {
							return false, err
						}
						if err := service.SetMotorForward(
							ctx,
							MotorTurningSpeed,
						); err != nil {
							return false, err
						}

						// Log that the robot is turning right
						if loggerProducer != nil {
							loggerProducer.Info("Turning right...")
						}
					}

					// Check if the robot can collide with an object or a wall
					cardinalDirections := getFrontDistanceCardinalDirections(isTurning)
					reached, err := collisionHandler(
						ctx,
						service,
						isTurning,
						loggerProducer,
						cardinalDirections...,
					)
					if err != nil {
						return false, err
					}
					if reached {
						// Set that the turn is completed
						isTurningCompleted = true
						break
					}
				case true:
					// Check if it's turning
					if !isTurning {
						if !wallCloseUp && northDistance+northDistanceChange >= FrontCloseupThreshold {
							if err := service.SetMotorForward(
								ctx,
								MotorForwardSlowSpeed,
							); err != nil {
								return false, err
							}
							if err := service.SetServoToCenter(ctx); err != nil {
								return false, err
							}
							wallCloseUp = true

							// Log that the robot is moving forward to get close to the wall
							if loggerProducer != nil {
								loggerProducer.Info("Moving forward to get close to the wall...")
							}
							continue
						}

						// If the robot is not close to the wall, center by gyroscope while moving forward
						if wallCloseUp && northDistance+northDistanceChange > FrontCloseupThreshold {
							if err := centerByGyroscopeHandler(
								ctx,
								service,
								last90DegreeTurns,
								loggerProducer,
							); err != nil {
								return false, err
							}
							continue
						}

						// If the robot is close to the wall, start turning left
						if err := service.SetServoToLeft(
							ctx,
							ServoBigTurnAngle,
						); err != nil {
							return false, err
						}
						if err := service.SetMotorBackward(
							ctx,
							MotorBackwardSlowSpeed,
						); err != nil {
							return false, err
						}

						// Log that the robot is turning left
						if loggerProducer != nil {
							loggerProducer.Info("Turning left...")
						}

						// Sets the turning state to true
						isTurning = true
						continue
					}

					// Wait for back close up to finish the turn
					if err := backCloseUpHandler(
						ctx,
						service,
						loggerProducer,
					); err != nil {
						return false, err
					}

					// Set that the turn is completed
					isTurningCompleted = true
				}
			case gorplidarsdkhandler.CardinalDirectionWest:
				// Handle it based on the inner lane side
				switch *isInnerLaneSide {
				case false:
					// Handle a normal turn
					if !isTurning {
						if err := service.SetServoToLeft(
							ctx,
							ServoBigTurnAngle,
						); err != nil {
							return false, err
						}
						if err := service.SetMotorForward(
							ctx,
							MotorTurningSpeed,
						); err != nil {
							return false, err
						}

						// Log that the robot is turning left
						if loggerProducer != nil {
							loggerProducer.Info("Turning left...")
						}
					}

					// Check if the robot can collide with an object or a wall
					cardinalDirections := getFrontDistanceCardinalDirections(isTurning)
					reached, err := collisionHandler(
						ctx,
						service,
						isTurning,
						loggerProducer,
						cardinalDirections...,
					)
					if err != nil {
						return false, err
					}
					if reached {
						// Set that the turn is completed
						isTurningCompleted = true
						break
					}
				case true:
					// Check if it's turning
					if !isTurning {
						if !wallCloseUp && northDistance+northDistanceChange >= FrontCloseupThreshold {
							if err := service.SetMotorForward(
								ctx,
								MotorForwardSlowSpeed,
							); err != nil {
								return false, err
							}
							if err := service.SetServoToCenter(ctx); err != nil {
								return false, err
							}
							wallCloseUp = true

							// Log that the robot is moving forward to get close to the wall
							if loggerProducer != nil {
								loggerProducer.Info("Moving forward to get close to the wall...")
							}
							continue
						}

						// If the robot is not close to the wall, center by gyroscope while moving forward
						if wallCloseUp && northDistance+northDistanceChange > FrontCloseupThreshold {
							if err := centerByGyroscopeHandler(
								ctx,
								service,
								last90DegreeTurns,
								loggerProducer,
							); err != nil {
								return false, err
							}
							continue
						}

						// If the robot is close to the wall, start turning right
						if err := service.SetServoToRight(
							ctx,
							ServoMediumTurnAngle,
						); err != nil {
							return false, err
						}
						if err := service.SetMotorBackward(
							ctx,
							MotorBackwardSlowSpeed,
						); err != nil {
							return false, err
						}

						// Log that the robot is turning right
						if loggerProducer != nil {
							loggerProducer.Info("Turning right...")
						}

						// Sets the turning state to true
						isTurning = true
					}

					// Wait for back close up to finish the turn
					if err := backCloseUpHandler(
						ctx,
						service,
						loggerProducer,
					); err != nil {
						return false, err
					}

					// Set that the turn is completed
					isTurningCompleted = true
				}
			default:
				// If the cardinal direction is not set, return
				return false, fmt.Errorf(
					"invalid cardinal direction to turn in turnByWallCloseUpHandler: %s",
					toCardinalDirection.String(),
				)
			}
		}
	}

	// Update the last turning time
	*lastTurningTime = time.Now()

	// Log that the turn is completed
	if loggerProducer != nil {
		loggerProducer.Info("Turn completed.")
	}

	return true, nil
}
