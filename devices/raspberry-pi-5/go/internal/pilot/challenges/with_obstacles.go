package challenges

import (
	"context"
	"fmt"
	"math"
	"time"

	goconcurrentlogger "github.com/ralvarezdev/go-concurrent-logger"
	gorplidarsdkhandler "github.com/ralvarezdev/go-rplidar-sdk-handler"
	internalclip "github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal/clip"
)

const (

	// ParkingLeaveSideDistanceThreshold is the distance threshold to leave the parking (only used in the closed challenge)
	ParkingLeaveSideDistanceThreshold = 500.0

	// StopBackwardDirectionOnParkingBackwardDistanceThreshold is the distance threshold to stop the backward direction when leaving parking (only used in the closed challenge)
	StopBackwardDirectionOnParkingBackwardDistanceThreshold = 290.0

	// StopForwardDirectionOnParkingFrontDistanceThreshold is the distance threshold to go forward for the first time when leaving parking (only used in the closed challenge)
	StopForwardDirectionOnParkingFrontDistanceThreshold = 95.0

	// LeftParkingSideDistanceThreshold is the distance threshold for the left side sensor when leaving parking (only used in the closed challenge)
	LeftParkingSideDistanceThreshold = 450.0

	// ObjectDetectionInTheSameSectionDelay is the delay to consider an object detection in the same section (only used in the closed challenge)
	ObjectDetectionInTheSameSectionDelay = 3 * time.Second
)

type (
	// ChallengeWithObstaclesHandler is the type for the challenge with obstacles handler
	ChallengeWithObstaclesHandler struct {
		service               Service
		logger                goconcurrentlogger.Logger
		handlerLoggerProducer goconcurrentlogger.LoggerProducer
		debug                 bool
	}
)

// NewChallengeWithObstaclesHandler is the handler for the challenge with obstacles
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
func NewChallengeWithObstaclesHandler(
	service Service,
	logger goconcurrentlogger.Logger,
	debug bool,
) (*ChallengeWithObstaclesHandler, error) {
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
func (h *ChallengeWithObstaclesHandler) Run(
	ctx context.Context,
	parking bool,
) error {
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
	h.handlerLoggerProducer.Info("Starting challenge with obstacles")

	// Wait until the service is ready
	if err = h.service.WaitUntilReady(ctx); err != nil {
		return fmt.Errorf("service is not ready: %w", err)
	}

	// Leave the parking
	if parking {
		if err = h.leaveParkingHandler(ctx); err != nil {
			return fmt.Errorf("failed to leave parking: %w", err)
		}
	}

	// Initialize positive label and sections obstacles
	var sectionsObstacles [4][2]internalclip.PositiveLabel
	for i := range sectionsObstacles {
		for j := range sectionsObstacles[i] {
			sectionsObstacles[i][j] = internalclip.PositiveLabelNil
		}
	}

	// Initialize variables
	var (
		isObjectAvoidanceInProgress bool
		currentSectionObstacleCount int
		last90DegreeTurns           int
		lastTurningTime             time.Time
		lastUpdateTime              time.Time
		lastObjectDetectionTime     time.Time
	)

	// Run until the robot has completed the required number of 90 degree turns
	for last90DegreeTurns < Algorithm90DegreeTurns {
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

			// Check if the robot is avoiding an obstacle
			positiveLabel, err := avoidObstacles(
				ctx,
				h.service,
				&isObjectAvoidanceInProgress,
				h.handlerLoggerProducer,
			)
			{
				if err != nil {
					return err
				}
				if isObjectAvoidanceInProgress {
					// Check if the object detection is in the same section
					if lastObjectDetectionTime.IsZero() || time.Since(lastObjectDetectionTime) >= ObjectDetectionInTheSameSectionDelay {
						// Add the positive label to the sections obstacles
						sectionIndex := last90DegreeTurns % 4

						// If it's not the first full road completion, corroborate the obstacle
						if last90DegreeTurns >= 4 {
							// Check if the obstacle is the same as the initial one
							if sectionsObstacles[sectionIndex][currentSectionObstacleCount] == internalclip.PositiveLabelNil {
								sectionsObstacles[sectionIndex][currentSectionObstacleCount] = positiveLabel
							}

							// If the obstacle is different from the initial one, log it
							if sectionsObstacles[sectionIndex][currentSectionObstacleCount] != positiveLabel {
								h.handlerLoggerProducer.Warning(
									fmt.Sprintf(
										"Different obstacle detected in section %d: %s (was %s)",
										sectionIndex+1,
										positiveLabel.String(),
										sectionsObstacles[sectionIndex][currentSectionObstacleCount].String(),
									),
								)
							}
							currentSectionObstacleCount++
						}
					}
					break
				}

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
	}

	// Log that is almost time to stop
	h.handlerLoggerProducer.Info("Almost time to stop. Monitoring front distance...")

	// Set the servo to center and the motor to slow speed
	if err := h.service.SetServoToCenter(ctx); err != nil {
		return err
	}
	if err := h.service.SetMotorForward(
		ctx,
		MotorForwardSlowSpeed,
	); err != nil {
		return err
	}

	// Wait until the front distance is below the stop distance threshold
	var completed bool
	for !completed {
		// Wait for the RPLiDAR to update
		time.Sleep(UpdateDelay)

		select {
		case <-ctx.Done():
			return ctx.Err()
		default:
			// Get the north distance and its change
			northDistance := h.service.GetRPLiDARAverageDistance(gorplidarsdkhandler.CardinalDirectionNorth)
			northDistanceChange := h.service.GetRPLiDARAverageDistanceChange(gorplidarsdkhandler.CardinalDirectionNorth)

			// Check if any measure is NaN
			if math.IsNaN(northDistance) || math.IsNaN(northDistanceChange) {
				continue
			}

			// Check if the north distance is below the stop distance threshold
			if northDistance <= StopDistanceThreshold {
				completed = true
				h.handlerLoggerProducer.Info("Challenge completed successfully. Stopping the robot.")
			}
		}
	}

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
		MotorBackwardSlowSpeed,
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
			ServoBigTurnAngle,
		); err != nil {
			return err
		}
	case ServoDirectionRight:
		if err := h.service.SetServoToRight(
			ctx,
			ServoBigTurnAngle,
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
		MotorForwardSlowSpeed,
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
			if parkingLeaveSide != ServoDirectionLeft && parkingLeaveSide != ServoDirectionRight {
				return false, fmt.Errorf(
					"invalid parking leave side: %w",
					ErrInvalidServoDirection,
				)
			}

			// Wait until the opposite distance is not NaN
			oppositeCardinalDirection := parkingLeaveSide.OppositeCardinalDirection()
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
			westDistance := h.service.GetWestAverageDistance()
			eastDistance := h.service.GetEastAverageDistance()

			// Check if any of the sides has the space to leave the parking
			if !math.IsNaN(westDistance) && westDistance >= ParkingLeaveSideDistanceThreshold {
				parkingLeaveSide = ServoDirectionLeft
			} else if !math.IsNaN(eastDistance) && eastDistance >= ParkingLeaveSideDistanceThreshold {
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
				FrontDistanceTurningCardinalDirections...,
			)
			if err != nil {
				return fmt.Errorf(
					"failed to wait for front distance threshold on parking: %w",
					err,
				)
			}
			leftParkingCompleted = left
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
