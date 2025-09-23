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

	// SideDistanceThreshold is the distance threshold for side sensors
	SideDistanceThreshold = 1750.0

	// FrontStartTurnDistanceThreshold is the distance threshold to start turning
	FrontStartTurnDistanceThreshold = 1000.0 // 500.0, 600.0, 650.0, 900.0
)

type (
	// ChallengeWithoutObstaclesHandler is the type for the challenge without obstacles handler
	ChallengeWithoutObstaclesHandler struct {
		service               Service
		logger                goconcurrentlogger.Logger
		handlerLoggerProducer goconcurrentlogger.LoggerProducer
		debug                 bool
		servoAngle            float64
		servoDirection        ServoDirection
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
	if err := h.service.WaitUntilReady(ctx); err != nil {
		return fmt.Errorf("service is not ready: %w", err)
	}

	// Start the challenge without obstacles handler
	var isTurning bool
	var last90DegreeTurns uint
	var lastIterationTime time.Time
	var lastTurningTime time.Time
	direction := ServoDirectionNil
	for last90DegreeTurns < Algorithm90DegreeTurns {
		// Set the last iteration time
		time.Sleep(UpdateDelay - time.Since(lastIterationTime))
		lastIterationTime = time.Now()

		select {
		case <-ctx.Done():
			return ctx.Err()
		default:
			// Check if the front distance is below the safety threshold
			reached, err := safetyFrontDistanceHandler(
				ctx,
				h.service,
				h.handlerLoggerProducer,
				isTurning,
				gorplidarsdkhandler.CardinalDirectionNorthwest,
				gorplidarsdkhandler.CardinalDirectionNorthNorthwest,
				gorplidarsdkhandler.CardinalDirectionNorth,
				gorplidarsdkhandler.CardinalDirectionNorthNortheast,
				gorplidarsdkhandler.CardinalDirectionNortheast,
			)
			if err != nil {
				return err
			}
			if reached {
				break
			}

			// Check for the current turn and center the servo if necessary
			turnCompleted, err := turnHandler(
				ctx,
				h.service,
				&last90DegreeTurns,
				&isTurning,
				&lastTurningTime,
				&direction,
				h.handlerLoggerProducer,
			)
			if err != nil {
				return err
			}
			if turnCompleted {
				break
			}

			// Detect if a turn is necessary
			if err := detectTurnHandler(
				ctx,
				h.service,
				&last90DegreeTurns,
				&isTurning,
				&lastTurningTime,
				&direction,
			); err != nil {
				return err
			}
			if isTurning {
				break
			}

			// Center by gyroscope
			if err = centerByGyroscopeHandler(
				ctx,
				h.service,
				last90DegreeTurns,
			); err != nil {
				return err
			}

			// Move forward
			motorSpeed := MotorForwardNormalPercentage
			if h.servoDirection == ServoDirectionStraight && time.Since(lastTurningTime) >= MinTimeToCorrectAfterTurn {
				motorSpeed = MotorForwardFastPercentage
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
	if err := h.service.SetServoToCenter(ctx); err != nil {
		return err
	}
	if err := h.service.SetMotorForward(
		ctx,
		MotorForwardNormalPercentage,
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
			// Check if the north average distance is NaN
			if math.IsNaN(h.service.GetNorthAverageDistance()) {
				break
			}

			// Get the rate of change for the north average distance
			northDistanceChange := FrontDistanceChange * h.service.GetRPLiDARAverageDistanceChange(gorplidarsdkhandler.CardinalDirectionNorth)

			// Check if the north average distance is below the stop distance threshold
			if h.service.GetNorthAverageDistance()+northDistanceChange <= StopDistanceThreshold {
				completed = true
				h.handlerLoggerProducer.Info("Challenge completed successfully. Stopping the robot.")
			}
		}
	}
	return nil
}
