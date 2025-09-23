package challenges

import (
	"context"
	"fmt"	
	"math"
	"time"

	gorplidarsdkhandler "github.com/ralvarezdev/go-rplidar-sdk-handler"
	goconcurrentlogger "github.com/ralvarezdev/go-concurrent-logger"
)

type (
	// ChallengeWithObstaclesHandler is the type for the challenge with obstacles handler
	ChallengeWithObstaclesHandler struct {
		service Service
		logger goconcurrentlogger.Logger
		handlerLoggerProducer goconcurrentlogger.LoggerProducer
		debug bool
	}
)

// ChallengeWithObstaclesHandler is the handler for the challenge with obstacles
// 
// Parameters:
//
// service: The service to use for the challenge
// logger: The logger to use for logging messages
// debug: A boolean indicating if debug logging is enabled
//
// Returns:
//
// A pointer to the newly created ChallengeWithObstaclesHandler instance, or an error if the handler could not be created
func NewChallengeWithObstaclesHandler(service Service, logger goconcurrentlogger.Logger, debug bool) (*ChallengeWithObstaclesHandler, error) {
	// Check if the service is nil
	if service == nil {
		return nil, ErrNilService
	}

	// Check if the logger is nil
	if logger == nil {
		return nil, goconcurrentlogger.ErrNilLogger
	}

	return &ChallengeWithObstaclesHandler{
		service: service,
		logger:  logger,
		debug:   debug,
	}, nil
}

// Run handles the challenge with obstacles
//
// Parameters:
//
// ctx: The context to use for the challenge
// parking: A boolean indicating if the challenge includes parking
//
// Returns:
//
// An error if the challenge could not be handled, nil otherwise
func (h *ChallengeWithObstaclesHandler) Run(ctx context.Context, parking bool) error {
	// Create a logger producer for the handler
	handlerLoggerProducer, err := h.logger.NewProducer(ChallengeHandlerLoggerProducerTag, h.debug)
	if err != nil {
		return fmt.Errorf("failed to create handler logger producer: %w", err)
	}
	h.handlerLoggerProducer = handlerLoggerProducer
	defer h.handlerLoggerProducer.Close()

	// Log the start of the challenge
	h.handlerLoggerProducer.Info("Starting challenge with obstacles")

	// Wait until the service is ready
	if err := h.service.WaitUntilReady(ctx); err != nil {
		return fmt.Errorf("service is not ready: %w", err)
	}
	
	// Leave the parking
	if parking {
	if err := h.leaveParkingHandler(ctx); err != nil {
		return fmt.Errorf("failed to leave parking: %w", err)
	}
}

	/*
		var WallCloseUp bool
		var isTurning bool
		var bno08xLast90DegreeTurns int
		var westAverageDistance, eastAverageDistance, northAverageDistance, northNortheastAverageDistance, northNorthwestAverageDistance float64
		for h.usbCDCHandler.Get90DegreeTurns() < Algorithm90DegreeTurns {
			// Sleep the RPLiDAR delay to wait for new measures
			time.Sleep(RPLiDARDelay - time.Since(h.rplidarLastMeasuresUpdateTime))

			select {
			case <-ctx.Done():
				return ctx.Err()
			default:
				// Update the RPLiDAR average distances
				if err := h.updateRPLiDARAverageDistances(); err != nil {
					return fmt.Errorf(
						"failed to update RPLiDAR average distances: %w",
						err,
					)
				}
				westAverageDistance = h.getAverageDirectionDistance(gorplidarsdkhandler.CardinalDirectionWest)
				eastAverageDistance = h.getAverageDirectionDistance(gorplidarsdkhandler.CardinalDirectionEast)
				northAverageDistance = h.getAverageDirectionDistance(gorplidarsdkhandler.CardinalDirectionNorth)
				northNortheastAverageDistance = h.getAverageDirectionDistance(gorplidarsdkhandler.CardinalDirectionNorthNortheast)
				northNorthwestAverageDistance = h.getAverageDirectionDistance(gorplidarsdkhandler.CardinalDirectionNorthNorthwest)

				// Log the average distances
				h.handlerLoggerProducer.Info(
					fmt.Sprintf(
						"W: %f, N-NW: %f, N: %f, N-NE: %f, E: %f",
						westAverageDistance,
						northNorthwestAverageDistance,
						northAverageDistance,
						northNortheastAverageDistance,
						eastAverageDistance,
					),
				)

				// Check if the front distance is below the safety threshold
				if !WallCloseUp {
					if northAverageDistance < SafetyFrontDistanceStartThreshold || northNortheastAverageDistance < SafetyFrontDistanceStartThreshold || northNorthwestAverageDistance < SafetyFrontDistanceStartThreshold {
						previousServoAngle := h.servoAngle
						previousServoDirection := h.servoDirection
						previousMotorSpeed := h.motorSpeed

						// Log the warning
						h.handlerLoggerProducer.Warning(
							fmt.Sprintf(
								"Front distance is below the safety threshold %f.",
								SafetyFrontDistanceStartThreshold,
							),
						)

						// Set the servo to center and the motor to backward
						if err := h.setServoToCenter(ctx); err != nil {
							return fmt.Errorf("failed to set servo to center: %w", err)
						}

						if err := h.setMotorBackwardByPercentage(
							ctx,
							MotorBackwardSlowPercentage,
						); err != nil {
							return fmt.Errorf(
								"failed to set motor to backward: %w",
								err,
							)
						}

						var safe bool
						for !safe {
							// Sleep the RPLiDAR delay to wait for new measures
							time.Sleep(RPLiDARDelay - time.Since(h.rplidarLastMeasuresUpdateTime))

							select {
							case <-ctx.Done():
								return ctx.Err()
							default:
								// Update the RPLiDAR average distances
								if err := h.updateRPLiDARAverageDistances(); err != nil {
									return fmt.Errorf(
										"failed to update RPLiDAR average distances: %w",
										err,
									)
								}
								northAverageDistance = h.getAverageDirectionDistance(gorplidarsdkhandler.CardinalDirectionNorth)
								northNortheastAverageDistance = h.getAverageDirectionDistance(gorplidarsdkhandler.CardinalDirectionNorthNortheast)
								northNorthwestAverageDistance = h.getAverageDirectionDistance(gorplidarsdkhandler.CardinalDirectionNorthNorthwest)

								if northAverageDistance >= SafetyFrontDistanceStopThreshold && northNortheastAverageDistance >= SafetyFrontDistanceStopThreshold && northNorthwestAverageDistance >= SafetyFrontDistanceStopThreshold {
									h.handlerLoggerProducer.Info("Safety front distance threshold reached.")
									safe = true
								}
							}
						}
					}
					// Set previous servo angle and motor speed back to normal
					if isTurning {
						if err := h.setServoAngle(
							ctx,
							previousServoAngle,
							previousServoDirection,
						); err != nil {
							return fmt.Errorf(
								"failed to set servo to previous angle and direction: %w",
								err,
							)
						}
					} else {
						if err := h.setServoToOppositeDirection(
							ctx,
							previousServoAngle,
						); err != nil {
							return fmt.Errorf(
								"failed to set servo to opposite direction: %w",
								err,
							)
						}
					}
					if err := h.setMotorSpeed(
						ctx,
						previousMotorSpeed,
						MotorDirectionForward,
					); err != nil {
						return fmt.Errorf(
							"failed to set motor to previous speed: %w",
							err,
						)
					}
					continue
				}

				// Check for the current turn and center the servo if necessary
				if isTurning {
					// Get the latest BNO08x turns value
					turns := h.usbCDCHandler.Get90DegreeTurns()
					if turns > bno08xLast90DegreeTurns {
						h.handlerLoggerProducer.Info(
							fmt.Sprintf(
								"Detected a turn. Current turns: %d, Last turns: %d",
								turns,
								bno08xLast90DegreeTurns,
							),
						)

						// Center the servo
						if err := h.setServoToCenter(ctx); err != nil {
							return fmt.Errorf(
								"failed to set servo to center: %w",
								err,
							)
						}

						// Update for the next check
						bno08xLast90DegreeTurns = turns
						isTurning = false
					}
					continue
				}
				/*
				// Check if the robot should move forward or turn
				if northAverageDistance >= FrontStartTurnDistanceThreshold {
					var motorSpeedPercentage float64
					if northNortheastAverageDistance >= FrontStartTurnDistanceThreshold && northNorthwestAverageDistance >= FrontStartTurnDistanceThreshold {
						motorSpeedPercentage = MotorForwardFastPercentage
					} else {
						motorSpeedPercentage = MotorForwardNormalPercentage
					}

					// Move forward
					if err := h.setMotorForwardByPercentage(
						ctx,
						motorSpeedPercentage,
					); err != nil {
						return fmt.Errorf(
							"failed to set motor to forward speed: %w",
							err,
						)
					}

					// Check if the servo should make a little turn to the left or right in order to center the robot
					if eastAverageDistance >= westAverageDistance*(1+SideDistanceDifferencePercentage) {
						if err := h.setServoToRightByPercentage(
							ctx,
							ServoSmallTurnAnglePercentage,
						); err != nil {
							return fmt.Errorf(
								"failed to set servo to small right turn: %w",
								err,
							)
						}
					} else if westAverageDistance >= eastAverageDistance*(1+SideDistanceDifferencePercentage) {
						if err := h.setServoToLeftByPercentage(
							ctx,
							ServoSmallTurnAnglePercentage,
						); err != nil {
							return fmt.Errorf(
								"failed to set servo to small left turn: %w",
								err,
							)
						}
					} else {
						if err := h.setServoToCenter(ctx); err != nil {
							return fmt.Errorf(
								"failed to set servo to center: %w",
								err,
							)
						}
					}
					continue
				}
	*/
	/*
				if err := h.setMotorForwardByPercentage(
					ctx,
					MotorForwardNormalPercentage,
				); err != nil {
					return fmt.Errorf(
						"failed to set motor to normal speed: %w",
						err,
					)
				}

				// Check if the robot should turn left or right based on the side distances
				if eastAverageDistance >= SideDistanceThreshold {
					TemporaryTurns = bno08xLast90DegreeTurns
					isTurning = true

				 //Checks which lane is the robot located inside

					if westAverageDistance >= float64(LaneIdentifierThreshold) && isTurning == true {
						if northAverageDistance >= FrontCloseupThreshold {
							if err := h.setMotorForwardByPercentage(
								ctx,
								MotorForwardSlowPercentage,
							); err != nil {
								return fmt.Errorf(
									"failed to set motor to normal speed: %w",
									err,
								)
							}
							if err := h.setServoToCenter(ctx); err != nil {
								return fmt.Errorf(
									"failed to set servo to center: %w",
									err,
								)
							}
							WallCloseUp = true
						}
						if northAverageDistance <= float64(FrontCloseupThreshold) && WallCloseUp == true {
							if err := h.setServoToLeftByPercentage(
								ctx,
								ServoMediumTurnAnglePercentage,
							); err != nil {
								return fmt.Errorf(
									"failed to set servo to small left turn: %w",
									err,
								)
							}
							if err := h.setMotorBackwardByPercentage(
								ctx,
								MotorBackwardSlowPercentage,
							); err != nil {
								return fmt.Errorf(
									"failed to set motor to normal speed: %w",
									err,
								)
							}

							// Basically this condition is meant to indicate when has the robot successfully made the turn (if its not enough, we can stop the turn at like 60 degrees or smth, then counteract the other 30 degrees while going backwards)
							if bno08xLast90DegreeTurns != TemporaryTurns {
								isTurning = false
								WallCloseUp = false
								continue
							}
						}
					else {
					    if err := h.setServoToRightByPercentage(
							ctx,
							ServoMediumTurnAnglePercentage,
						); err != nil {
							return fmt.Errorf(
								"failed to set servo to small right turn: %w",
								err,
							)
						}
						if err := h.setMotorForwardByPercentage(
							ctx,
							MotorForwardSlowPercentage,
						); err != nil {
							return fmt.Errorf(
								"failed to set motor to normal speed: %w",
								err,
							)
						}
							// Basically this condition is meant to indicate when has the robot successfully made the turn
							if bno08xLast90DegreeTurns != TemporaryTurns {
								if err := h.setServoToRightByPercentage(
									ctx,
									ServoMediumTurnAnglePercentage,
								); err != nil {
									return fmt.Errorf(
										"failed to set servo to small right turn: %w",
										err,
									)
								}
								if err := h.setMotorBackwardByPercentage(
									ctx,
									MotorBackwardSlowPercentage,
								); err != nil {
									return fmt.Errorf(
										"failed to set motor to normal speed: %w",
										err,
									)
								}
								if (1 == 1) { // keeps doing it until it reaches the wall (prob measurements with the rplidar)
									h.servoDirection = ServoDirectionStraight}
								isTurning = false
					}	}	}
				}
				else if westAverageDistance >= SideDistanceThreshold {
					TemporaryTurns = bno08xLast90DegreeTurns
					isTurning = true

					// Checks which lane is the robot located inside

					if eastAverageDistance >= float64(LaneIdentifierThreshold) && isTurning == true {
						if northAverageDistance >= FrontCloseupThreshold {
							if err := h.setMotorForwardByPercentage(
								ctx,
								MotorForwardSlowPercentage,
							); err != nil {
								return fmt.Errorf(
									"failed to set motor to normal speed: %w",
									err,
								)
							}
							if err := h.setServoToCenter(ctx); err != nil {
								return fmt.Errorf(
									"failed to set servo to center: %w",
									err,
								)
							}
							WallCloseUp = true
						}
						if northAverageDistance <= float64(FrontCloseupThreshold) && WallCloseUp == true {
							if err := h.setServoToRightByPercentage(
								ctx,
								ServoMediumTurnAnglePercentage,
							); err != nil {
								return fmt.Errorf(
									"failed to set servo to small right turn: %w",
									err,
								)
							}
							if err := h.setMotorBackwardByPercentage(
								ctx,
								MotorBackwardSlowPercentage,
							); err != nil {
								return fmt.Errorf(
									"failed to set motor to normal speed: %w",
									err,
								)
							}

							// Basically this condition is meant to indicate when has the robot successfully made the turn
							if bno08xLast90DegreeTurns != TemporaryTurns {
								isTurning = false
								WallCloseUp = false
								continue
							}
						}
					else {
					    if err := h.setServoToLeftByPercentage(
							ctx,
							ServoMediumTurnAnglePercentage,
						); err != nil {
							return fmt.Errorf(
								"failed to set servo to small left turn: %w",
								err,
							)
						}
						if err := h.setMotorBackwardByPercentage(
							ctx,
							MotorBackwardSlowPercentage,
						); err != nil {
							return fmt.Errorf(
								"failed to set motor to normal speed: %w",
								err,
							)
						}
							// Basically this condition is meant to indicate when has the robot successfully made the turn
							if bno08xLast90DegreeTurns != TemporaryTurns {
								if err := h.setServoToLeftByPercentage(
									ctx,
									ServoMediumTurnAnglePercentage,
								); err != nil {
									return fmt.Errorf(
										"failed to set servo to small left turn: %w",
										err,
									)
								}
								if err := h.setMotorBackwardByPercentage(
									ctx,
									MotorBackwardSlowPercentage,
								); err != nil {
									return fmt.Errorf(
										"failed to set motor to normal speed: %w",
										err,
									)
								}
								// keeps doing it until it reaches the wall (prob measurements with the rplidar)
								if err := h.setServoToCenter(ctx); err != nil {
									return fmt.Errorf(
										"failed to set servo to center: %w",
										err,
									)
								}
								isTurning = false
						}	}
					}
				}

				// After each turn, the robot starts looking for the objects (it should be roughly centered, and it could gather the objects position, (left or right lane) with the rplidar)

				if !isTurning {
					for i := 180; i < 360; i++ {
						if h.rplidarHandler.GetMeasures(i) <= CameraRangeThreshold {
							if h.clipClassification == red_block {
								if err := h.setServoToRightByPercentage(
									ctx,
									ServoMediumTurnAnglePercentage,
								); err != nil {
									return fmt.Errorf(
										"failed to set servo to small right turn: %w",
										err,
									)
								}
								if err := h.setMotorForwardByPercentage(
									ctx,
									MotorForwardNormalPercentage,
								); err != nil {
									return fmt.Errorf(
										"failed to set motor to normal speed: %w",
										err,
									)
								}
								if westAverageDistance <= float64(CameraRangeThreshold) && eastAverageDistance <= float64(CameraRangeThreshold) {
									if err := h.setServoToRightByPercentage(
										ctx,
										ServoMediumTurnAnglePercentage,
									); err != nil {
										return fmt.Errorf(
											"failed to set servo to small right turn: %w",
											err,
										)
									}
								}
								else if northAverageDistance <= float64(FrontCloseupThreshold) {
									if err := h.setServoToCenter(ctx); err != nil {
										return fmt.Errorf(
											"failed to set servo to center: %w",
											err,
										)
									}
									if err := h.setMotorBackwardByPercentage(
										ctx,
										MotorBackwardNormalPercentage,
									); err != nil {
										return fmt.Errorf(
											"failed to set motor to normal speed: %w",
											err,
										)
									}
									return
								}
							}
							else if h.clipClassification == green_block {
								if err := h.setServoToLeftByPercentage(
									ctx,
									ServoMediumTurnAnglePercentage,
								); err != nil {
									return fmt.Errorf(
										"failed to set servo to small left turn: %w",
										err,
									)
								}
								if err := h.setMotorForwardByPercentage(
									ctx,
									MotorForwardNormalPercentage,
								); err != nil {
									return fmt.Errorf(
										"failed to set motor to normal speed: %w",
										err,
									)
								}
								if westAverageDistance <= float64(CameraRangeThreshold) and eastAverageDistance <= float64(CameraRangeThreshold) {
									while (robot not aligned)
									if err := h.setServoToRightByPercentage(
										ctx,
										ServoMediumTurnAnglePercentage,
									); err != nil {
										return fmt.Errorf(
											"failed to set servo to small right turn: %w",
											err,
										)
									}
						}
								else if northAverageDistance <= float64(FrontCloseupThreshold) {
									if err := h.setServoToCenter(ctx); err != nil {
										return fmt.Errorf(
											"failed to set servo to center: %w",
											err,
										)
									}
									if err := h.setMotorBackwardByPercentage(
										ctx,
										MotorBackwardNormalPercentage,
									); err != nil {
										return fmt.Errorf(
											"failed to set motor to normal speed: %w",
											err,
										)
									}
									continue
						} 			}
								}
							}
						}
					}
				}
			}

		// Log that is almost time to stop
		h.handlerLoggerProducer.Info("Almost time to stop. Monitoring front distance...")

		// Set the servo to center and the motor to slow speed
		if err := h.setServoToCenter(ctx); err != nil {
			return fmt.Errorf("failed to set servo to center: %w", err)
		}
		if err := h.setMotorForwardByPercentage(
			ctx,
			MotorForwardSlowPercentage,
		); err != nil {
			return fmt.Errorf(
				"failed to set motor to slow speed: %w",
				err,
			)
		}

		// Wait until the front distance is below the stop distance threshold
		var completed bool
		for !completed {
			// Wait for the RPLiDAR to update
			time.Sleep(RPLiDARDelay - time.Since(h.rplidarLastMeasuresUpdateTime))

			select {
			case <-ctx.Done():
				return ctx.Err()
			default:
				// Update the RPLiDAR average distances
				if err := h.updateRPLiDARAverageDistances(); err != nil {
					return fmt.Errorf(
						"failed to update RPLiDAR average distances: %w",
						err,
					)
				}
				northAverageDistance = h.getAverageDirectionDistance(gorplidarsdkhandler.CardinalDirectionNorth)

				if northAverageDistance <= StopDistanceThreshold {
					completed = true
					h.handlerLoggerProducer.Info("Challenge completed successfully. Stopping the robot.")
				}
			}
		}
	*/

	// Enter the parking
	if parking {
	if err := h.enterParkingHandler(ctx); err != nil {
		return fmt.Errorf("failed to enter parking: %w", err)
	}
}

	return nil
}

// goBackwardSlowlyOnParking makes the robot go backward slowly on the parking
//
// Parameters:
//
// ctx: The context to use for going backward slowly on the parking
//
// Returns:
//
// An error if the robot could not go backward slowly on the parking, nil otherwise
func (h *ChallengeWithObstaclesHandler) goBackwardSlowlyOnParking(ctx context.Context) error {
	// Center the servo
	if err := h.service.SetServoToCenter(ctx); err != nil {
		return err
	}
	// Set the motor to backward and the servo to the parking leave side
	if err := h.service.SetMotorBackward(
		ctx,
		MotorBackwardSlowPercentage,
	); err != nil {
		return err
	}

	// Wait until the front distance threshold to stop backward movement is reached
	var stopBackwardMovement bool
	for !stopBackwardMovement {
		time.Sleep(UpdateDelay)

		select {
		case <-ctx.Done():
			return ctx.Err()
		default:
			// Check if the front distance threshold to stop backward movement is reached
			frontDistances := []float64{
				h.service.GetSouthSoutheastAverageDistance(),
				h.service.GetSouthSouthwestAverageDistance(),
			}
			for _, distance := range frontDistances {
				// Check if the distance is NaN
				if math.IsNaN(distance) {
					continue
				}

				// Check if the distance is above the threshold
				if distance <= StopBackwardDirectionOnParkingBackwardDistanceThreshold {
					stopBackwardMovement = true
					break
				}
			}
		}
	}

	// Stop the motor
	if err := h.service.SetMotorStop(ctx); err != nil {
		return err
	}
	return nil
}

// setMotorAndServoToParkingLeaveSide sets the motor and servo to the parking leave side
//
// Parameters:
//
// ctx: The context to use for setting the motor and servo to the parking leave side
// parkingLeaveSide: The side to leave the parking (left or right)
//
// Returns:
//
// An error if the motor and servo could not be set to the parking leave side, nil otherwise
func (h *ChallengeWithObstaclesHandler) setMotorAndServoToParkingLeaveSide(
	ctx context.Context,
	parkingLeaveSide ServoDirection,
) error {
	// Set the servo to the parking leave side and the motor to forward slowly
	switch parkingLeaveSide {
	case ServoDirectionLeft:
		if err := h.service.SetServoToLeft(
			ctx,
			ServoBigTurnAnglePercentage,
		); err != nil {
			return err
		}
	case ServoDirectionRight:
		if err := h.service.SetServoToRight(
			ctx,
			ServoBigTurnAnglePercentage,
		); err != nil {
			return err
		}
	default:
		return fmt.Errorf(
			"invalid parking leave side: %w",
			ErrInvalidServoDirection,
		)
	}
	if err := h.service.SetMotorForward(
		ctx,
		MotorForwardSlowPercentage,
	); err != nil {
		return err
	}
	return nil
}

// goForwardSlowlyOnParking waits until the front distance threshold on parking is reached
//
// Parameters:
//
// ctx: The context to use for waiting for the front distance threshold on parking
// parkingLeaveSide: The side to leave the parking (left or right)
// cardinalDirections: The cardinal directions to consider for the front distance threshold on parking
//
// Returns:
//
// An error if the front distance threshold on parking could not be reached, nil otherwise
func (h *ChallengeWithObstaclesHandler) goForwardSlowlyOnParking(
	ctx context.Context,
	parkingLeaveSide ServoDirection,
	cardinalDirections ...gorplidarsdkhandler.CardinalDirection,
) (bool, error) {
	var frontDistanceThresholdReached bool
	for !frontDistanceThresholdReached {
		select {
		case <-ctx.Done():
			return false, ctx.Err()
		default:
			// Check if the opposite side of the parking leave side has reached the threshold for the parking to be considered left
			var oppositeCardinalDirection gorplidarsdkhandler.CardinalDirection
			switch parkingLeaveSide {
			case ServoDirectionLeft:
				oppositeCardinalDirection = gorplidarsdkhandler.CardinalDirectionEast
			case ServoDirectionRight:
				oppositeCardinalDirection = gorplidarsdkhandler.CardinalDirectionWest
			default:
				return false, fmt.Errorf(
					"invalid parking leave side: %w",
					ErrInvalidServoDirection,
				)
			}

			// Wait until the opposite distance is not NaN
			oppositeDistance := math.NaN()
			for {
				time.Sleep(UpdateDelay)

				select {
				case <-ctx.Done():
					return false, ctx.Err()
				default:
					// Get the opposite distance
					oppositeDistance = h.service.GetRPLiDARAverageDistance(oppositeCardinalDirection)
				}

				// Break the loop if the opposite distance is not NaN
				if !math.IsNaN(oppositeDistance) {
					break
				}
			}
			if oppositeDistance >= LeftParkingSideDistanceThreshold {
				h.handlerLoggerProducer.Info("Opposite side distance threshold on parking reached.")
				return true, nil
			}

			// Get the average distance for the cardinal directions
			for _, cardinalDirection := range cardinalDirections {
				distance := h.service.GetRPLiDARAverageDistance(cardinalDirection)

				// Check if any of the front distances is below the threshold
				if !math.IsNaN(distance) && distance <= StopForwardDirectionOnParkingFrontDistanceThreshold {
					frontDistanceThresholdReached = true
					h.handlerLoggerProducer.Info("Front distance threshold on parking reached.")
					break
				}
			}
		}
	}
	return false, nil
}

// leaveParkingHandler handles leaving the parking
//
// Parameters:
//
// ctx: The context to use for leaving the parking
//
// Returns:
//
// An error if the parking could not be left, nil otherwise
func (h *ChallengeWithObstaclesHandler) leaveParkingHandler(ctx context.Context) error {
	// Check which side has the space to leave the parking
	parkingLeaveSide := ServoDirectionNil
	for parkingLeaveSide == ServoDirectionNil {
		time.Sleep(UpdateDelay)

		select {
		case <-ctx.Done():
			return ctx.Err()
		default:
			// Get west and east average distances
			westAverageDistance := h.service.GetWestAverageDistance()
			eastAverageDistance := h.service.GetEastAverageDistance()

			// Check if any of the sides has the space to leave the parking
			if !math.IsNaN(westAverageDistance) && westAverageDistance >= ParkingLeaveSideDistanceThreshold {
				parkingLeaveSide = ServoDirectionLeft
			} else if !math.IsNaN(eastAverageDistance) && eastAverageDistance >= ParkingLeaveSideDistanceThreshold {
				parkingLeaveSide = ServoDirectionRight
			}
		}
	}

	// Iterate to leave the parking
	var leftParkingCompleted bool
	for !leftParkingCompleted {
		select {
		case <-ctx.Done():
			return ctx.Err()
		default:
			// Go backward slowly on the parking
			if err := h.goBackwardSlowlyOnParking(ctx); err != nil {
				return fmt.Errorf(
					"failed to go backward slowly on parking: %w",
					err,
				)
			}

			// Set the motor and servo to the parking leave side
			if err := h.setMotorAndServoToParkingLeaveSide(
				ctx,
				parkingLeaveSide,
			); err != nil {
				return fmt.Errorf(
					"failed to set motor and servo to parking leave side: %w",
					err,
				)
			}

			// Go forward slowly on the parking until the front distance threshold on parking is reached
			left, err := h.goForwardSlowlyOnParking(
				ctx,
				parkingLeaveSide,
				gorplidarsdkhandler.CardinalDirectionNorth,
				gorplidarsdkhandler.CardinalDirectionNorthNortheast,
				gorplidarsdkhandler.CardinalDirectionNorthNorthwest,
				gorplidarsdkhandler.CardinalDirectionNorthwest,
				gorplidarsdkhandler.CardinalDirectionNortheast,
			)
			if err != nil {
				return fmt.Errorf(
					"failed to wait for front distance threshold on parking: %w",
					err,
				)
			}
			if left {
				leftParkingCompleted = true
			}
		}
	}

	// Log that the parking has been left
	h.handlerLoggerProducer.Info("Parking left successfully.")

	// Center the servo and stop the motor
	if err := h.service.SetServoToCenter(ctx); err != nil {
		return err
	}
	if err := h.service.SetMotorStop(ctx); err != nil {
		return err
	}
	return nil
}

// enterParkingHandler handles entering the parking
//
// Parameters:
//
// ctx: The context to use for entering the parking
//
// Returns:
//
// An error if the parking could not be entered, nil otherwise
func (h *ChallengeWithObstaclesHandler) enterParkingHandler(ctx context.Context) error {
	for {
		select {
		case <-ctx.Done():
			return ctx.Err()
		default:
			return ErrNotImplemented
		}
	}
}