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
	// StopDistanceThreshold is the distance threshold to stop the robot
	StopDistanceThreshold = 1500.0
)

type (
	// ChallengeWithoutObstaclesHandler is the type for the challenge without obstacles handler
	ChallengeWithoutObstaclesHandler struct {
		service               Service
		logger                goconcurrentlogger.Logger
		handlerLoggerProducer goconcurrentlogger.LoggerProducer
		debug                 bool
		servoAngle            float64
		motorSpeed            float64
		motorDirection        float64
	}
)

// NewChallengeWithoutObstaclesHandler is the handler for the challenge without obstacles
//
// Parameters:
//
// service: The service to use for the challenge
// logger: The logger to use for logging messages
// debug: A boolean indicating if debug logging is enabled
//
// Returns:
//
// A pointer to the newly created ChallengeWithoutObstaclesHandler instance, or an error if the handler could not be created
func NewChallengeWithoutObstaclesHandler(
	service Service,
	logger goconcurrentlogger.Logger,
	debug bool,
) (*ChallengeWithoutObstaclesHandler, error) {
	// Check if the service is nil
	if service == nil {
		return nil, ErrNilService
	}

	// Check if the logger is nil
	if logger == nil {
		return nil, goconcurrentlogger.ErrNilLogger
	}

	return &ChallengeWithoutObstaclesHandler{
		service: service,
		logger:  logger,
		debug:   debug,
	}, nil
}

// Run handles the challenge without obstacles
//
// Parameters:
//
// ctx: The context to use for the challenge
//
// Returns:
//
// An error if the challenge could not be handled, nil otherwise
func (h *ChallengeWithoutObstaclesHandler) Run(ctx context.Context) error {
	// Create a logger producer for the handler
	handlerLoggerProducer, err := h.logger.NewProducer(
		ChallengeHandlerLoggerProducerTag,
		h.debug,
	)
	if err != nil {
		return fmt.Errorf("failed to create handler logger producer: %w", err)
	}
	h.handlerLoggerProducer = handlerLoggerProducer
	defer h.handlerLoggerProducer.Close()

	// Log the start of the challenge
	h.handlerLoggerProducer.Info("Starting challenge without obstacles")

	// Wait until the service is ready
	if err = h.service.WaitUntilReady(ctx); err != nil {
		return fmt.Errorf("service is not ready: %w", err)
	}

	// Start the challenge without obstacles handler
	direction := ServoDirectionNil
	var (
		isTurning         bool
		last90DegreeTurns int
		lastUpdateTime    time.Time
		lastTurningTime   time.Time
	)
	// direction := ServoDirectionNil
	for last90DegreeTurns < Algorithm90DegreeTurns {
		// Set the last iteration time
		time.Sleep(UpdateDelay - time.Since(lastUpdateTime))
		lastUpdateTime = time.Now()

		select {
		case <-ctx.Done():
			return ctx.Err()
		default:				
			// If the robot was turning, check if it should stop turning
			if isTurning {
				turnCompleted, err := turnCompletedHandler(
					ctx,
					h.service,
					last90DegreeTurns,
					h.handlerLoggerProducer,
				)
				if err != nil {
					return err
				}
				if turnCompleted {
					// Update the last turning time
					lastTurningTime = time.Now()

					// Update is turning flag
					isTurning = false

					// Increase 90-degree turns
					last90DegreeTurns++
					break
				}

				// Calculate the future distance based on the current distance change
				northDistance := h.service.GetRPLiDARAverageDistanceOnNextUpdate(
					gorplidarsdkhandler.CardinalDirectionNorth,
				)

				// Check if the front distance is NaN, if so, return
				if math.IsNaN(northDistance) {
					continue
				}


				// Check if the front distance is below the turn threshold
				if northDistance < SafetyFrontDistanceTurnThreshold {
					// Log that the front distance is too close
					if h.handlerLoggerProducer != nil {
						h.handlerLoggerProducer.Info(
							fmt.Sprintf(
								"Front distance (%.2f mm) is below the safety threshold (%.2f mm). Moving backward until it's safe to turn.",
								northDistance,
								SafetyFrontDistanceTurnThreshold,
							),
						)
					}
					if err := h.service.SetMotorStop(ctx); err != nil {
						return err
					}
					if err := h.service.SetServoToCenter(ctx); err != nil {
						return err
					}
					// Go backward if the front distance is below the threshold
					if err := h.service.SetMotorBackward(
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
							// Calculate the future distance based on the current distance change
							northDistance = h.service.GetRPLiDARAverageDistanceOnNextUpdate(
								gorplidarsdkhandler.CardinalDirectionNorth,
							)

							// Check if the front distance is NaN, if so, return
							if math.IsNaN(northDistance) {
								break
							}

							// If the front distance is above the threshold, stop moving backward
							if northDistance >= SafetyFrontDistanceTurnThreshold {
								if h.handlerLoggerProducer != nil {
									h.handlerLoggerProducer.Info("Front distance is safe to turn. Resuming turn.")
								}
								if err := h.service.SetMotorStop(ctx); err != nil {
									return err
								}

								// Set reached flag as true
								reached = true
							}
						}
					}
					

				// Set the servo to the turn angle
				if err := h.service.SetServoAngle(
					ctx,
					ServoBigTurnAngle,
					direction,
				); err != nil {
					return err
				}

				// Move forward at turning speed
				if err := h.service.SetMotorForward(
					ctx,
					MotorTurningSpeed,
				); err != nil {
					return err
				}
				break
			}
			} else {
				// Detect if a turn is necessary
				turnDetected, err := detectTurnHandler(
					ctx,
					h.service,
					last90DegreeTurns,
					lastTurningTime,
					&direction,
					h.handlerLoggerProducer,
				)
				if err != nil {
					return err
				}
				if turnDetected {
					// Update the is turning flag
					isTurning = true
					break
				}
			}

			// Center from gyroscope and RPLiDAR
			if err = centerFromSidesByRPLiDARAndGyroscopeHandler(
				ctx,
				h.service,
				lastTurningTime,
				last90DegreeTurns,
				h.handlerLoggerProducer,
			); err != nil {
				return err
			}

			// Move forward
			if err = h.service.SetMotorForward(
				ctx,
				MotorForwardFastSpeed,
			); err != nil {
				return err
			}
		}
	}

	// Log that is almost time to stop
	h.handlerLoggerProducer.Info("Almost time to stop. Monitoring front distance...")

	// Set the servo to center and the motor to slow speed
	if err = h.service.SetServoToCenter(ctx); err != nil {
		return err
	}
	if err = h.service.SetMotorForward(
		ctx,
		MotorForwardNormalSpeed,
	); err != nil {
		return err
	}

	// Wait until the front distance is below the stop distance threshold
	var completed bool
	for !completed {
		time.Sleep(UpdateDelay)

		select {
		case <-ctx.Done():
			return ctx.Err()
		default:
			// Center from gyroscope and RPLiDAR
			if err = centerFromSidesByRPLiDARAndGyroscopeHandler(
				ctx,
				h.service,
				lastTurningTime,
				last90DegreeTurns,
				h.handlerLoggerProducer,
			); err != nil {
				return err
			}

			// Calculate the future distance change based on the current distance change
			distance := h.service.GetRPLiDARAverageDistanceOnNextUpdate(
				gorplidarsdkhandler.CardinalDirectionNorth,
			)

			// Check if any measure is NaN
			if math.IsNaN(distance) {
				continue
			}

			// Check if the north distance is below the stop distance threshold
			if distance <= StopDistanceThreshold {
				completed = true
				h.handlerLoggerProducer.Info("Challenge completed successfully. Stopping the robot.")
			}
		}
	}
	return nil
}
