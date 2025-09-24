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
	var (
		// isTurning       bool
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
			// Handle turning by wall close up
			turned, err := turnByWallCloseUpHandler(
				ctx,
				h.service,
				&lastTurningTime,
				h.handlerLoggerProducer,
			)
			if err != nil {
				return err
			}
			if turned {
				// Update last 90 degree turns
				last90DegreeTurns++
				continue
			}

			// Check if the robot can collide with an object or a wall
			cardinalDirections := getFrontDistanceCardinalDirections(false)
			reached, err := collisionHandler(
				ctx,
				h.service,
				false,
				h.handlerLoggerProducer,
				cardinalDirections...,
			)
			if err != nil {
				return err
			}
			if reached {
				break
			}

			/*
				// Check if the robot can collide with an object or a wall
				cardinalDirections := getFrontDistanceCardinalDirections(isTurning)
				reached, err := collisionHandler(
					ctx,
					h.service,
					isTurning,
					h.handlerLoggerProducer,
					cardinalDirections...,
				)
				if err != nil {
					return err
				}
				if reached {
					break
				}

				// If the robot was turning, check if it should stop turning
				// Check for the current turn and center the servo if necessary
				turnCompleted, err := turnHandler(
					ctx,
					h.service,
					&last90DegreeTurns,
					&isTurning,
					&lastTurningTime,
					h.handlerLoggerProducer,
				)
				if err != nil {
					return err
				}
				if turnCompleted {
					break
				}

				// Detect if a turn is necessary
				if err = detectTurnHandler(
					ctx,
					h.service,
					&last90DegreeTurns,
					&isTurning,
					&lastTurningTime,
					&direction,
					h.handlerLoggerProducer,
				); err != nil {
					return err
				}
				if isTurning {
					break
				}
			*/

			// Center by gyroscope
			if err = centerByGyroscopeHandler(
				ctx,
				h.service,
				last90DegreeTurns,
				h.handlerLoggerProducer,
			); err != nil {
				return err
			}

			// Move forward
			motorSpeed := MotorForwardNormalSpeed
			servoDirection := h.service.GetServoDirection()
			if servoDirection == ServoDirectionStraight && time.Since(lastTurningTime) >= MinTimeToCorrectAfterTurn {
				motorSpeed = MotorForwardFastSpeed
			}
			if err = h.service.SetMotorForward(
				ctx,
				motorSpeed,
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
			// Center by gyroscope
			if err = centerByGyroscopeHandler(
				ctx,
				h.service,
				last90DegreeTurns,
				h.handlerLoggerProducer,
			); err != nil {
				return err
			}

			// Get the north distance and its change
			northDistance := h.service.GetNorthAverageDistance()
			northDistanceChange := FrontDistanceChange * h.service.GetRPLiDARAverageDistanceChange(gorplidarsdkhandler.CardinalDirectionNorth)

			// Check if any measure is NaN, if so, continue
			if math.IsNaN(northDistance) || math.IsNaN(northDistanceChange) {
				continue
			}

			// Check if the north average distance is below the stop distance threshold
			if northDistance+northDistanceChange <= StopDistanceThreshold {
				completed = true
				h.handlerLoggerProducer.Info("Challenge completed successfully. Stopping the robot.")
			}
		}
	}
	return nil
}
