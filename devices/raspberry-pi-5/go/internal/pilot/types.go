package pilot

import (
	"context"
	"errors"
	"fmt"
	"log"
	"os"
	"os/signal"
	"sync"
	"sync/atomic"
	"syscall"
	"time"

	"golang.org/x/sync/errgroup"

	goconcurrentlogger "github.com/ralvarezdev/go-concurrent-logger"
	gohailocliphandler "github.com/ralvarezdev/go-hailo-clip-handler"
	gorplidarsdkhandler "github.com/ralvarezdev/go-rplidar-sdk-handler"
	"github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal"
	internalusbcdc "github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal/usbcdc"
)

type (
	// DefaultHandler is the default implementation of the Handler interface
	DefaultHandler struct {
		mutex                         sync.Mutex
		handlerLoggerProducer         goconcurrentlogger.LoggerProducer
		logger                        goconcurrentlogger.Logger
		rplidarHandler                gorplidarsdkhandler.Handler
		clipHandler                   gohailocliphandler.Handler
		usbCDCHandler                 internalusbcdc.Handler
		usbCDCSender                  internalusbcdc.Sender
		isRunning                     atomic.Bool
		servoDirection                ServoDirection
		servoAngle                    uint16
		motorDirection                MotorDirection
		motorSpeed                    uint16
		rplidarMeasures               *[360]*gorplidarsdkhandler.Measure
		rplidarAverageDistances       map[gorplidarsdkhandler.CardinalDirection]float64
		rplidarLastMeasuresUpdateTime time.Time
		clipClassification            *gohailocliphandler.Classification
		maxMotorSpeedValue            uint16
		maxServoAngleValue            uint16
		debug                         bool
	}
)

// NewDefaultHandler creates a new instance of DefaultHandler
//
// Parameters:
//
// logger: The logger to use for logging messages.
// rplidarHandler: The RPLidar handler to use for getting distance measurements.
// clipHandler: The CLIP handler to use for controlling the robot's movement.
// usbCDCHandler: The USB-CDC handler to use for communication with the robot.
// debug: A boolean indicating if debug logging is enabled.
//
// Returns:
//
// A pointer to the newly created DefaultHandler instance, or an error if the handler could not be created.
func NewDefaultHandler(
	logger goconcurrentlogger.Logger,
	rplidarHandler gorplidarsdkhandler.Handler,
	clipHandler gohailocliphandler.Handler,
	usbCDCHandler internalusbcdc.Handler,
	debug bool,
) (*DefaultHandler, error) {
	// Check if the logger is nil
	if logger == nil {
		return nil, goconcurrentlogger.ErrNilLogger
	}

	// Check if the RPLiDAR handler is nil
	if rplidarHandler == nil {
		return nil, gorplidarsdkhandler.ErrNilHandler
	}

	// Check if the CLIP handler is nil
	if clipHandler == nil {
		return nil, gohailocliphandler.ErrNilHandler
	}

	// Check if the USB-CDC handler is nil
	if usbCDCHandler == nil {
		return nil, internalusbcdc.ErrNilHandler
	}

	return &DefaultHandler{
		logger:         logger,
		rplidarHandler: rplidarHandler,
		clipHandler:    clipHandler,
		usbCDCHandler:  usbCDCHandler,
		debug:          debug,
	}, nil
}

// IsRunning returns true if the handler is running, false otherwise
//
// Returns:
//
// A boolean indicating if the handler is running
func (h *DefaultHandler) IsRunning() bool {
	return h.isRunning.Load()
}

// setMotorSpeed sets the speed of the motor
//
// Parameters:
//
// ctx: The context to use for setting the motor speed
// speed: The speed to set the motor
// direction: The direction to set the motor
//
// Returns:
//
// An error if the speed could not be set, nil otherwise
func (h *DefaultHandler) setMotorSpeed(
	ctx context.Context,
	speed uint16,
	direction MotorDirection,
) error {
	// Check if it's the same speed and direction as the current one
	if h.motorDirection == direction && h.motorSpeed == speed {
		return nil
	}

	// Clear motor speed start and end messages channel
	h.usbCDCHandler.ClearMotorSpeedStartAndEndMessagesCh()

	// Update the motor direction and speed
	h.motorDirection = direction
	h.motorSpeed = speed

	// Send the outgoing message to set the motor speed
	var receivedStartMessage bool
	for range SetMotorSpeedAttempts {
		switch direction {
		case MotorDirectionStop:
			// Log the motor stop action
			h.handlerLoggerProducer.Info(
				"Setting motor speed to 0, stopping the motor",
			)
			if err := h.usbCDCSender.SendMessage(
				internalusbcdc.OutgoingMotorSpeedStopMessage,
			); err != nil {
				return err
			}
		case MotorDirectionForward:
			h.handlerLoggerProducer.Info(
				fmt.Sprintf(
					"Setting motor speed to %d in forward direction",
					speed,
				),
			)
			if err := h.usbCDCSender.SendMessage(
				internalusbcdc.NewOutgoingMessageFromUint16Data(
					internalusbcdc.OutgoingCategoryMotorSpeedForward,
					speed,
				),
			); err != nil {
				return err
			}
		case MotorDirectionBackward:
			h.handlerLoggerProducer.Info(
				fmt.Sprintf(
					"Setting motor speed to %d in backward direction",
					speed,
				),
			)
			if err := h.usbCDCSender.SendMessage(
				internalusbcdc.NewOutgoingMessageFromUint16Data(
					internalusbcdc.OutgoingCategoryMotorSpeedBackward,
					speed,
				),
			); err != nil {
				return err
			}
		default:
			return ErrInvalidMotorDirection
		}

		// Wait for the start message with a timeout
		ctx, cancel := context.WithTimeout(
			ctx,
			MotorSpeedStartMessageTimeout,
		)
		if err := h.usbCDCHandler.WaitMotorSpeedStartMessage(ctx); err != nil {
			cancel()
			continue
		}

		// Set the flag to true and break the loop
		receivedStartMessage = true
		cancel()
		break
	}

	// Check if the start message was received
	if !receivedStartMessage {
		return ErrDidNotReceiveMotorSpeedStartMessage
	}

	// Create the context with timeout
	ctx, stop := context.WithTimeout(ctx, MotorSpeedEndMessageTimeout)
	defer stop()

	// Wait for the motor speed end message
	if err := h.usbCDCHandler.WaitMotorSpeedEndMessage(ctx); err != nil && !errors.Is(
		err,
		context.DeadlineExceeded,
	) {
		return err
	}
	return nil
}

// setMotorSpeedByPercentage sets the motor speed by percentage of the maximum motor speed value
//
// Parameters:
//
// ctx: The context to use for setting the motor speed
// percentage: The percentage of the maximum motor speed value to set the motor
// direction: The direction to set the motor
//
// Returns:
//
// An error if the speed could not be set, nil otherwise
func (h *DefaultHandler) setMotorSpeedByPercentage(
	ctx context.Context,
	percentage float64,
	direction MotorDirection,
) error {
	if h.maxMotorSpeedValue == 0 {
		return ErrMaxMotorSpeedValueNotSet
	}

	speed := uint16(float64(h.maxMotorSpeedValue) * percentage)
	return h.setMotorSpeed(ctx, speed, direction)
}

// setMotorStop stops the motor
//
// Parameters:
//
// ctx: The context to use for setting the motor speed
//
// Returns:
//
// An error if the motor could not be stopped, nil otherwise
func (h *DefaultHandler) setMotorStop(ctx context.Context) error {
	if err := h.setMotorSpeed(ctx, 0, MotorDirectionStop); err != nil {
		return fmt.Errorf("failed to stop motor: %w", err)
	}
	return nil
}

// setMotorForwardByPercentage sets the motor speed to forward by percentage of the maximum motor speed value
//
// Parameters:
//
// ctx: The context to use for setting the motor speed
// percentage: The percentage of the maximum motor speed value to set the motor
//
// Returns:
//
// An error if the speed could not be set, nil otherwise
func (h *DefaultHandler) setMotorForwardByPercentage(
	ctx context.Context,
	percentage float64,
) error {
	if err := h.setMotorSpeedByPercentage(ctx, percentage, MotorDirectionForward); err != nil {
		return fmt.Errorf("failed to set motor to forward: %w", err)
	}
	return nil
}

// setMotorBackwardByPercentage sets the motor speed to backward by percentage of the maximum motor speed value
//
// Parameters:
//
// ctx: The context to use for setting the motor speed
// percentage: The percentage of the maximum motor speed value to set the motor
//
// Returns:
//
// An error if the speed could not be set, nil otherwise
func (h *DefaultHandler) setMotorBackwardByPercentage(
	ctx context.Context,
	percentage float64,
) error {
	if err := h.setMotorSpeedByPercentage(ctx, percentage, MotorDirectionBackward); err != nil {
		return fmt.Errorf("failed to set motor to backward: %w", err)
	}
	return nil
}

// setServoAngle sets the servo direction
//
// Parameters:
//
// ctx: The context to use for setting the servo angle
// angle: The angle to set the servo
// direction: The direction to set the servo
//
// Returns:
//
// An error if the servo direction could not be set, nil otherwise
func (h *DefaultHandler) setServoAngle(
	ctx context.Context,
	angle uint16,
	direction ServoDirection,
) error {
	// Check if the servo direction and angle is the same as the current one
	if h.servoDirection == direction && h.servoAngle == angle {
		return nil
	}

	// Clear servo angle start and end messages channel
	h.usbCDCHandler.ClearServoAngleStartAndEndMessagesCh()

	// Update the servo direction and angle
	h.servoDirection = direction
	h.servoAngle = angle

	// Send the outgoing message to set the angle speed
	var receivedStartMessage bool
	for range SetServoAngleAttempts {
		switch direction {
		case ServoDirectionStraight:
			h.handlerLoggerProducer.Info("Setting servo direction to center")
			if err := h.usbCDCSender.SendMessage(
				internalusbcdc.OutgoingServoAngleCenterMessage,
			); err != nil {
				return err
			}
		case ServoDirectionLeft:
			h.handlerLoggerProducer.Info(
				fmt.Sprintf(
					"Setting servo direction to left with angle %d",
					angle,
				),
			)
			if err := h.usbCDCSender.SendMessage(
				internalusbcdc.NewOutgoingMessageFromUint16Data(
					internalusbcdc.OutgoingCategoryServoAngleToLeft,
					angle,
				),
			); err != nil {
				return err
			}
		case ServoDirectionRight:
			h.handlerLoggerProducer.Info(
				fmt.Sprintf(
					"Setting servo direction to right with angle %d",
					angle,
				),
			)
			if err := h.usbCDCSender.SendMessage(
				internalusbcdc.NewOutgoingMessageFromUint16Data(
					internalusbcdc.OutgoingCategoryServoAngleToRight,
					angle,
				),
			); err != nil {
				return err
			}
		default:
			return ErrInvalidServoDirection
		}

		// Wait for the start message with a timeout
		ctx, cancel := context.WithTimeout(
			ctx,
			ServoAngleStartMessageTimeout,
		)
		if err := h.usbCDCHandler.WaitServoAngleStartMessage(ctx); err != nil {
			cancel()
			continue
		}

		// Set the flag to true and break the loop
		receivedStartMessage = true
		cancel()
		break
	}

	// Check if the start message was received
	if !receivedStartMessage {
		return ErrDidNotReceiveServoAngleStartMessage
	}

	// Create the context with timeout
	ctx, stop := context.WithTimeout(ctx, ServoAngleEndMessageTimeout)
	defer stop()

	// Wait for the servo angle end message
	if err := h.usbCDCHandler.WaitServoAngleEndMessage(ctx); err != nil && !errors.Is(
		err,
		context.DeadlineExceeded,
	) {
		return err
	}
	return nil
}

// setServoAngleByPercentage sets the servo direction by percentage of the maximum servo direction value
//
// Parameters:
//
// ctx: The context to use for setting the servo angle
// percentage: The percentage of the maximum servo direction value to set the servo
// direction: The direction to set the servo
//
// Returns:
//
// An error if the servo direction could not be set, nil otherwise
func (h *DefaultHandler) setServoAngleByPercentage(
	ctx context.Context,
	percentage float64,
	direction ServoDirection,
) error {
	if h.maxServoAngleValue == 0 {
		return ErrMaxServoAngleValueNotSet
	}

	angle := uint16(float64(h.maxServoAngleValue) * percentage)
	return h.setServoAngle(ctx, angle, direction)
}

// setServoToCenter sets the servo to the center position
//
// Parameters:
//
// ctx: The context to use for setting the servo angle
//
// Returns:
//
// An error if the servo could not be set to center, nil otherwise
func (h *DefaultHandler) setServoToCenter(ctx context.Context) error {
	if err := h.setServoAngle(ctx, 90, ServoDirectionStraight); err != nil {
		return fmt.Errorf("failed to set servo to center: %w", err)
	}
	return nil
}

// setServoToLeft sets the servo to the left direction
//
// Parameters:
//
// ctx: The context to use for setting the servo angle
// angle: The angle to set the servo
//
// Returns:
//
// An error if the servo could not be set to left, nil otherwise
func (h *DefaultHandler) setServoToLeft(
	ctx context.Context,
	angle uint16,
) error {
	if err := h.setServoAngle(ctx, angle, ServoDirectionLeft); err != nil {
		return fmt.Errorf("failed to set servo to left: %w", err)
	}
	return nil
}

// setServoToLeftByPercentage sets the servo to the left direction by percentage of the maximum servo direction value
//
// Parameters:
//
// ctx: The context to use for setting the servo angle
// percentage: The percentage of the maximum servo direction value to set the servo
//
// Returns:
//
// An error if the servo could not be set to left, nil otherwise
func (h *DefaultHandler) setServoToLeftByPercentage(
	ctx context.Context,
	percentage float64,
) error {
	if err := h.setServoAngleByPercentage(ctx, percentage, ServoDirectionLeft); err != nil {
		return fmt.Errorf("failed to set servo to left: %w", err)
	}
	return nil
}

// setServoToRight sets the servo to the right direction
//
// Parameters:
//
// ctx: The context to use for setting the servo angle
// angle: The angle to set the servo
//
// Returns:
//
// An error if the servo could not be set to right, nil otherwise
func (h *DefaultHandler) setServoToRight(
	ctx context.Context,
	angle uint16,
) error {
	if err := h.setServoAngle(ctx, angle, ServoDirectionRight); err != nil {
		return fmt.Errorf("failed to set servo to right: %w", err)
	}
	return nil
}

// setServoToRightByPercentage sets the servo to the right direction by percentage of the maximum servo direction value
//
// Parameters:
//
// ctx: The context to use for setting the servo angle
// percentage: The percentage of the maximum servo direction value to set the servo
//
// Returns:
//
// An error if the servo could not be set to right, nil otherwise
func (h *DefaultHandler) setServoToRightByPercentage(
	ctx context.Context,
	percentage float64,
) error {
	if err := h.setServoAngleByPercentage(ctx, percentage, ServoDirectionRight); err != nil {
		return fmt.Errorf("failed to set servo to right: %w", err)
	}
	return nil
}

// setServoToOppositeDirection sets the servo to the opposite direction
//
// Parameters:
//
// ctx: The context to use for setting the servo angle
// servoAngle: The angle to set the servo. If 0, the servo will be set to center
//
// Returns:
//
// An error if the servo could not be set to the opposite direction, nil otherwise
func (h *DefaultHandler) setServoToOppositeDirection(
	ctx context.Context,
	servoAngle uint16,
) error {
	switch h.servoDirection {
	case ServoDirectionRight:
		return h.setServoToLeft(ctx, servoAngle)
	case ServoDirectionLeft:
		return h.setServoToRight(ctx, servoAngle)
	case ServoDirectionStraight:
		return h.setServoToCenter(ctx)
	default:
		return ErrInvalidServoDirection
	}
}

// updateCLIPClassification retrieves the latest CLIP classification
//
// Returns:
//
// An error if the classification could not be retrieved
func (h *DefaultHandler) updateCLIPClassification() error {
	// Update the CLIP classification
	clipClassification, err := h.clipHandler.GetClassification()
	if err != nil {
		return fmt.Errorf("failed to get CLIP classification: %w", err)
	}
	h.clipClassification = clipClassification
	return nil
}

// updateRPLiDARAverageDistances updates the average distances from the RPLiDAR measures
//
// Returns:
//
// An error if the average distances could not be updated, nil otherwise
func (h *DefaultHandler) updateRPLiDARAverageDistances() error {
	// Calculate the average north, west and east distances
	averageDistances, err := h.rplidarHandler.GetAverageDistancesFromAllDirections(
		AverageAngleWidth,
	)
	if err != nil {
		return fmt.Errorf(
			"average distances could not be calculated: %w",
			err,
		)
	}

	// Set the average distances and the last update time
	h.rplidarAverageDistances = averageDistances
	h.rplidarLastMeasuresUpdateTime = time.Now()
	return nil
}

// getAverageDirectionDistance gets the average distance for a specific direction
//
// Parameters:
//
// direction: The direction to get the average distance for
//
// Returns:
//
// The average distance for the specified direction, or 0.0 if the direction is not found
func (h *DefaultHandler) getAverageDirectionDistance(
	direction gorplidarsdkhandler.CardinalDirection,
) float64 {
	if h.rplidarAverageDistances == nil {
		return 0.0
	}

	// Get the average distance for the specified direction
	distance, ok := h.rplidarAverageDistances[direction]
	if !ok {
		return 0.0
	}
	return distance
}

// challengeWithObstaclesHandler handles the challenge with obstacles
//
// Parameters:
//
// ctx: The context to use for the challenge
//
// Returns:
//
// An error if the challenge could not be handled, nil otherwise
func (h *DefaultHandler) challengeWithObstaclesHandler(ctx context.Context) error {
	var WallCloseUp bool
	var isTurning bool
	var bno08xLastTurns int
	var westAverageDistance, eastAverageDistance, northAverageDistance, northNortheastAverageDistance, northNorthwestAverageDistance float64
	for h.usbCDCHandler.GetTurns() < AlgorithmTurns {
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
				turns := h.usbCDCHandler.GetTurns()
				if turns > bno08xLastTurns {
					h.handlerLoggerProducer.Info(
						fmt.Sprintf(
							"Detected a turn. Current turns: %d, Last turns: %d",
							turns,
							bno08xLastTurns,
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
					bno08xLastTurns = turns
					isTurning = false
				}
				continue
			}

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
				if err := h.setServoToRightByPercentage(
					ctx,
					ServoBigTurnAnglePercentage,
				); err != nil {
					return fmt.Errorf(
						"failed to set servo to big right turn: %w",
						err,
					)
				}
				isTurning = true
				if westAverageDistance >= float64(LaneIdentifierThreshold) {
					if northAverageDistance >= FrontCloseupThreshold {
						h.motorSpeed = MotorForwardSlowPercentage
						h.servoDirection = ServoDirectionCenter
						WallCloseUp = true
					}
					if northAverageDistance <= float64(FrontCloseupThreshold) && WallCloseUp == true {
						h.servoDirection = ServoDirectionLeft
						h.motorSpeed = MotorBackwardSlowPercentage
						h.motorSpeed = uint16(MotorForwardNormalPercentage)
					}
				} 
			} else if westAverageDistance >= SideDistanceThreshold {
				if err := h.setServoToLeftByPercentage(
					ctx,
					ServoBigTurnAnglePercentage,
				); err != nil {
					return fmt.Errorf(
						"failed to set servo to big left turn: %w",
						err,
					)
				}
				isTurning = true
				if eastAverageDistance >= float64(LaneIdentifierThreshold) {
					if northAverageDistance >= FrontCloseupThreshold {
						h.motorSpeed = MotorForwardSlowPercentage
						h.servoDirection = ServoDirectionCenter
						WallCloseUp = true
					}
					if northAverageDistance <= float64(FrontCloseupThreshold) && WallCloseUp == true {
						h.servoDirection = ServoDirectionRight
						h.motorSpeed = MotorBackwardSlowPercentage
						h.motorSpeed = uint16(MotorForwardNormalPercentage)
					}
				} 
			}

			// After each turn, the robot starts looking for the objects (it should be roughly centered, and it could gather the objects position, (left, center or right) with the rplidar)

			if !isTurning {
				for i := 180; i < 360; i++ {
					if h.rplidarHandler.GetMeasures(i) <= CameraRangeThreshold {
						h.clipHandler.GetClassification()
						if h.clipClassification == red_block {
							h.servoDirection = ServoDirectionRight
							h.motorSpeed = uint16(MotorForwardNormalPercentage)
							if westAverageDistance <= float64(CameraRangeThreshold) && eastAverageDistance <= float64(CameraRangeThreshold {
								h.servoDirection == ServoDirectionLeft
							}
							else if northAverageDistance <= float64(FrontCloseupThreshold) {
								h.servoDirection = ServoDirectionCenter
								h.motorSpeed = uint16(MotorBackwardNormalPercentage)
								continue
							}
						else if h.clipClassification == green_block {
							h.servoDirection = ServoDirectionLeft
							h.motorSpeed = uint16(MotorForwardNormalPercentage)
							if westAverageDistance <= float64(CameraRangeThreshold) and eastAverageDistance <= float64(CameraRangeThreshold)
								while (robot not aligned)
								h.servoDirection = ServoDirectionRight
							else if northAverageDistance <= float64(FrontCloseupThreshold)
								h.servoDirection = ServoDirectionCenter
								h.motorSpeed = uint16(MotorBackwardNormalPercentage)
								continue
							}
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
func (h *DefaultHandler) goBackwardSlowlyOnParking(ctx context.Context) error {
	// Center the servo
	if err := h.setServoToCenter(ctx); err != nil {
		return err
	}
	// Set the motor to backward and the servo to the parking leave side
	if err := h.setMotorBackwardByPercentage(
		ctx,
		MotorBackwardSlowPercentage,
	); err != nil {
		return err
	}

	// Wait until the front distance threshold to stop backward movement is reached
	var stopBackwardMovement bool
	for !stopBackwardMovement {
		// Sleep the RPLiDAR delay to wait for new measures
		time.Sleep(RPLiDARDelay - time.Since(h.rplidarLastMeasuresUpdateTime))

		select {
		case <-ctx.Done():
			return ctx.Err()
		default:
			// Update the RPLiDAR average distances
			if err := h.updateRPLiDARAverageDistances(); err != nil {
				return err
			}
			northAverageDistance := h.getAverageDirectionDistance(gorplidarsdkhandler.CardinalDirectionNorth)
			northNortheastAverageDistance := h.getAverageDirectionDistance(gorplidarsdkhandler.CardinalDirectionNorthNortheast)
			northNorthwestAverageDistance := h.getAverageDirectionDistance(gorplidarsdkhandler.CardinalDirectionNorthNorthwest)

			// Log the average distances
			h.handlerLoggerProducer.Info(
				fmt.Sprintf(
					"N-NW: %f, N: %f, N-NE: %f",
					northNorthwestAverageDistance,
					northAverageDistance,
					northNortheastAverageDistance,
				),
			)

			// Check if the front distance threshold to stop backward movement is reached
			frontDistances := []float64{
				northNortheastAverageDistance,
				northNorthwestAverageDistance,
				northAverageDistance,
			}
			for _, distance := range frontDistances {
				if distance >= StopBackwardDirectionOnParkingFrontDistanceThreshold {
					stopBackwardMovement = true
					break
				}
			}
		}
	}

	// Stop the motor
	if err := h.setMotorStop(ctx); err != nil {
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
func (h *DefaultHandler) setMotorAndServoToParkingLeaveSide(ctx context.Context, parkingLeaveSide ServoDirection) error {
	// Set the servo to the parking leave side and the motor to forward slowly
	switch parkingLeaveSide {
	case ServoDirectionLeft:
		if err := h.setServoToLeftByPercentage(
			ctx,
			ServoBigTurnAnglePercentage,
		); err != nil {
			return err
		}
	case ServoDirectionRight:
		if err := h.setServoToRightByPercentage(
			ctx,
			ServoBigTurnAnglePercentage,
		); err != nil {
			return err
		}
	default:
		return fmt.Errorf("invalid parking leave side: %w", ErrInvalidServoDirection)
	}
	if err := h.setMotorForwardByPercentage(
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
func (h *DefaultHandler) goForwardSlowlyOnParking(ctx context.Context, parkingLeaveSide ServoDirection, cardinalDirections... gorplidarsdkhandler.CardinalDirection) (bool, error) {
	var frontDistanceThresholdReached bool
	for !frontDistanceThresholdReached {
		// Sleep the RPLiDAR delay to wait for new measures
		time.Sleep(RPLiDARDelay - time.Since(h.rplidarLastMeasuresUpdateTime))

		select {
		case <-ctx.Done():
			return false, ctx.Err()
		default:
			// Update the RPLiDAR average distances
			if err := h.updateRPLiDARAverageDistances(); err != nil {
				return false, err
			}

			// Check if the opposite side of the parking leave side has reached the threshold for the parking to be considered left
			var oppositeCardinalDirection gorplidarsdkhandler.CardinalDirection
			switch parkingLeaveSide {
			case ServoDirectionLeft:
				oppositeCardinalDirection = gorplidarsdkhandler.CardinalDirectionEast
			case ServoDirectionRight:
				oppositeCardinalDirection = gorplidarsdkhandler.CardinalDirectionWest
			default:
				return false, fmt.Errorf("invalid parking leave side: %w", ErrInvalidServoDirection)
			}
			oppositeDistance := h.getAverageDirectionDistance(oppositeCardinalDirection)
			if oppositeDistance >= LeftParkingSideDistanceThreshold {
				h.handlerLoggerProducer.Info("Opposite side distance threshold on parking reached.")
				return true, nil
			}

			// Get the average distance for the cardinal directions
			for _, cardinalDirection := range cardinalDirections {
				distance := h.getAverageDirectionDistance(cardinalDirection)
				
				// Check if any of the front distances is below the threshold
				if distance <= StopForwardDirectionOnParkingFrontDistanceThreshold {
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
func (h *DefaultHandler) leaveParkingHandler(ctx context.Context) error {
	// Sleep the RPLiDAR delay to wait for new measures
	time.Sleep(RPLiDARDelay)

	// Update the RPLiDAR average distances
	if err := h.updateRPLiDARAverageDistances(); err != nil {
		return err
	}

	// Get west and east average distances
	westAverageDistance := h.getAverageDirectionDistance(gorplidarsdkhandler.CardinalDirectionWest)
	eastAverageDistance := h.getAverageDirectionDistance(gorplidarsdkhandler.CardinalDirectionEast)

	// Check which side has the space to leave the parking
	parkingLeaveSide := ServoDirectionNil
	if westAverageDistance >= ParkingLeaveSideDistanceThreshold {
		parkingLeaveSide = ServoDirectionLeft
	} else if eastAverageDistance >= ParkingLeaveSideDistanceThreshold {
		parkingLeaveSide = ServoDirectionRight
	} else {
		return ErrNoSpaceToLeaveParking
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
	if err := h.setServoToCenter(ctx); err != nil {
		return err
	}
	if err := h.setMotorStop(ctx); err != nil {
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
func (h *DefaultHandler) enterParkingHandler(ctx context.Context) error {
	for {
		select {
		case <-ctx.Done():
			return ctx.Err()
		default:
			return ErrNotImplemented
		}
	}
}


// challengeWithObstaclesAndParkingHandler handles the challenge with obstacles and parking
//
// Parameters:
//
// ctx: The context to use for the challenge
//
// Returns:
//
// An error if the challenge could not be handled, nil otherwise
func (h *DefaultHandler) challengeWithObstaclesAndParkingHandler(ctx context.Context) error {
	// Leave the parking
	if err := h.leaveParkingHandler(ctx); err != nil {
		return fmt.Errorf("failed to leave parking: %w", err)
	}

	// Handle the challenge with obstacles
	if err := h.challengeWithObstaclesHandler(ctx); err != nil {
		return fmt.Errorf("failed to handle challenge with obstacles: %w", err)
	}

	// Enter the parking
	if err := h.enterParkingHandler(ctx); err != nil {
		return fmt.Errorf("failed to enter parking: %w", err)
	}
	return nil
}

// safetyFrontDistanceOnChallengeWithObstaclesHandler handles the safety front distance reached on challenge with obstacles
//
// Parameters:
//
// ctx: The context to use for the challenge
// isTurning: A flag indicating if the robot is currently turning
// cardinalDirections: The cardinal directions to check the front distances (e.g., North, North-Northeast, North-Northwest)
//
// Returns:
//
// A boolean indicating if the safety front distance was handled, and an error if the safety front distance could not be handled, nil otherwise
func (h *DefaultHandler) safetyFrontDistanceOnChallengeWithObstaclesHandler(ctx context.Context, isTurning bool, cardinalDirections... gorplidarsdkhandler.CardinalDirection) (bool, error) {
	// Check if any of the front distances is below the safety threshold
	safetyFrontDistanceThresholdReached := false
	for _, cardinalDirection := range cardinalDirections {
		// Get the average distance for the cardinal direction
		distance := h.getAverageDirectionDistance(cardinalDirection)

		// If the distance is above or equal to the threshold, continue to the next direction
		if distance >= SafetyFrontDistanceStartThreshold {
			h.handlerLoggerProducer.Info(
				fmt.Sprintf(
					"%s cardinal direction front distance %f is above the safety threshold %f.",
					cardinalDirection.String(),
					distance,
					SafetyFrontDistanceStartThreshold,
				),
			)
			continue
		}

		// Set the flag to true
		safetyFrontDistanceThresholdReached = true
		break
	}
	if !safetyFrontDistanceThresholdReached {
		return false, nil
	}

	// Save previous servo angle, direction and motor speed
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
		return true, err
	}

	if err := h.setMotorBackwardByPercentage(
		ctx,
		MotorBackwardFastPercentage,
	); err != nil {
		return true, err
	}

	var safe bool
	for !safe {
		// Sleep the RPLiDAR delay to wait for new measures
		time.Sleep(RPLiDARDelay - time.Since(h.rplidarLastMeasuresUpdateTime))

		select {
		case <-ctx.Done():
			return true, ctx.Err()
		default:
			// Update the RPLiDAR average distances
			if err := h.updateRPLiDARAverageDistances(); err != nil {
				return true, err
			}

			// Check if the front distance threshold to stop backward movement is reached
			frontDistanceThresholdReached := true
			for _, cardinalDirection := range cardinalDirections {
				// Get the average distance for the cardinal direction
				distance := h.getAverageDirectionDistance(cardinalDirection)

				// If the distance is below the stop threshold, set the flag to false and break the loop
				if distance < SafetyFrontDistanceStopThreshold {
					frontDistanceThresholdReached = false
					break
				}
			}

			if frontDistanceThresholdReached {
				h.handlerLoggerProducer.Info("Safety front distance threshold reached.")
				safe = true
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
			return true, err
		}
	} else if err := h.setServoToOppositeDirection(
		ctx,
		previousServoAngle,
		); err != nil {
		return true, err
		}
	if err := h.setMotorSpeed(
		ctx,
		previousMotorSpeed,
		MotorDirectionForward,
	); err != nil {
		return true, err
	}
	return true, nil
}

// challengeWithoutObstaclesHandler handles the challenge without obstacles
//
// Parameters:
//
// ctx: The context to use for the challenge
//
// Returns:
//
// An error if the challenge could not be handled, nil otherwise
func (h *DefaultHandler) challengeWithoutObstaclesHandler(ctx context.Context) error {
	var isTurning bool
	var bno08xLastTurns int
	for h.usbCDCHandler.GetTurns() < AlgorithmTurns {
		// Sleep the RPLiDAR delay to wait for new measures
		if !h.rplidarLastMeasuresUpdateTime.IsZero() {
			time.Sleep(RPLiDARDelay - time.Since(h.rplidarLastMeasuresUpdateTime))
		} else {
			time.Sleep(RPLiDARDelay)
		}

		select {
		case <-ctx.Done():
			return ctx.Err()
		default:
			// Update the RPLiDAR average distances
			if err := h.updateRPLiDARAverageDistances(); err != nil {
				return err
			}
			// Check if the front distance is below the safety threshold
			reached, err := h.safetyFrontDistanceOnChallengeWithObstaclesHandler(
				ctx,
				isTurning,
				gorplidarsdkhandler.CardinalDirectionNortheast,
				gorplidarsdkhandler.CardinalDirectionNorthNorthwest,
				gorplidarsdkhandler.CardinalDirectionNorth,
				gorplidarsdkhandler.CardinalDirectionNorthNortheast,
				gorplidarsdkhandler.CardinalDirectionNorthNorthwest,
			)
			if err != nil {
				return err
			}
			if reached {
				continue
			}

			// Check for the current turn and center the servo if necessary
			if isTurning {
				// Get the latest BNO08x turns value
				turns := h.usbCDCHandler.GetTurns()
				if turns > bno08xLastTurns {
					h.handlerLoggerProducer.Info(
						fmt.Sprintf(
							"Detected a turn. Current turns: %d, Last turns: %d",
							turns,
							bno08xLastTurns,
						),
					)

					// Center the servo
					if err = h.setServoToCenter(ctx); err != nil {
						return err
					}

					// Update for the next check
					bno08xLastTurns = turns
					isTurning = false
				}
				continue
			}

			// Get west, east and front average distances
			westAverageDistance := h.getAverageDirectionDistance(gorplidarsdkhandler.CardinalDirectionWest)
			eastAverageDistance := h.getAverageDirectionDistance(gorplidarsdkhandler.CardinalDirectionEast)
			northAverageDistance := h.getAverageDirectionDistance(gorplidarsdkhandler.CardinalDirectionNorth)
			northNortheastAverageDistance := h.getAverageDirectionDistance(gorplidarsdkhandler.CardinalDirectionNorthNortheast)
			northNorthwestAverageDistance := h.getAverageDirectionDistance(gorplidarsdkhandler.CardinalDirectionNorthNorthwest)

			// Check if the robot should move forward or turn
			if northAverageDistance >= FrontStartTurnDistanceThreshold {
				var motorSpeedPercentage float64
				if northNortheastAverageDistance >= FrontStartTurnDistanceThreshold && northNorthwestAverageDistance >= FrontStartTurnDistanceThreshold {
					motorSpeedPercentage = MotorForwardFastPercentage
				} else {
					motorSpeedPercentage = MotorForwardNormalPercentage
				}

				// Check if the servo should make a little turn to the left or right in order to center the robot
				if eastAverageDistance >= westAverageDistance*(1+SideDistanceDifferencePercentage) {
					if err = h.setServoToRightByPercentage(
						ctx,
						ServoSmallTurnAnglePercentage,
					); err != nil {
						return err
					}
				} else if westAverageDistance >= eastAverageDistance*(1+SideDistanceDifferencePercentage) {
					if err = h.setServoToLeftByPercentage(
						ctx,
						ServoSmallTurnAnglePercentage,
					); err != nil {
						return err
					}
				} else if err = h.setServoToCenter(ctx); err != nil {
					return err
				}

				// Move forward
				if err = h.setMotorForwardByPercentage(
					ctx,
					motorSpeedPercentage,
				); err != nil {
					return err
				}
				continue
			}

			// Check if the robot should turn left or right based on the side distances
			if eastAverageDistance >= SideDistanceThreshold {
				isTurning = true
				h.servoDirection = ServoDirectionRight
			} else if westAverageDistance >= SideDistanceThreshold {
				isTurning = true
				h.servoDirection = ServoDirectionLeft
			}
			if isTurning {
				if err = h.setServoAngleByPercentage(
					ctx,
					ServoBigTurnAnglePercentage,
					h.servoDirection,
				); err != nil {
					return err
				}
			}

			// Move forward at normal speed
			if err = h.setMotorForwardByPercentage(
				ctx,
				MotorForwardNormalPercentage,
			); err != nil {
				return err
			}
		}
	}

	// Log that is almost time to stop
	h.handlerLoggerProducer.Info("Almost time to stop. Monitoring front distance...")

	// Set the servo to center and the motor to slow speed
	if err := h.setServoToCenter(ctx); err != nil {
		return err
	}
	if err := h.setMotorForwardByPercentage(
		ctx,
		MotorForwardSlowPercentage,
	); err != nil {
		return err
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
				return err
			}
			northAverageDistance := h.getAverageDirectionDistance(gorplidarsdkhandler.CardinalDirectionNorth)

			if northAverageDistance <= StopDistanceThreshold {
				completed = true
				h.handlerLoggerProducer.Info("Challenge completed successfully. Stopping the robot.")
			}
		}
	}
	return nil
}

// runToWrap is the internal function to run the pilot handler
//
// Parameters:
//
// ctx: Context for managing cancellation and timeouts.
//
// Returns:
//
// An error if the pilot could not be run, nil otherwise
func (h *DefaultHandler) runToWrap(ctx context.Context) error {
	// Initialize the USB-CDC sender
	usbCDCSender, err := h.usbCDCHandler.NewSender()
	if err != nil {
		return fmt.Errorf("failed to create USB-CDC sender: %w", err)
	}
	h.usbCDCSender = usbCDCSender
	defer func() {
		// Log the closure
		h.handlerLoggerProducer.Info("Closing USB-CDC sender...")

		// Close the sender
		h.usbCDCSender.Close()

		// Log the closure
		h.handlerLoggerProducer.Info("USB-CDC sender closed")
	}()

	// Wait for the challenge message to be set
	h.handlerLoggerProducer.Info("Waiting for challenge message...")
	challenge, err := h.usbCDCHandler.WaitForChallenge(ctx)
	if err != nil {
		return fmt.Errorf("failed to wait for challenge message: %w", err)
	}
	h.handlerLoggerProducer.Info(
		fmt.Sprintf("Challenge message received: %s", challenge.String()),
	)

	// Wait for max motor speed value to be set
	h.handlerLoggerProducer.Info("Waiting for max motor speed value...")
	maxMotorSpeed, err := h.usbCDCHandler.WaitForMaxMotorSpeedValue(ctx)
	if err != nil {
		return fmt.Errorf("failed to wait for max motor speed value: %w", err)
	}
	h.handlerLoggerProducer.Info(
		fmt.Sprintf("Max motor speed value received: %d", maxMotorSpeed),
	)
	h.maxMotorSpeedValue = maxMotorSpeed

	// Wait for max servo direction value to be set
	h.handlerLoggerProducer.Info("Waiting for max servo direction value...")
	maxServoAngle, err := h.usbCDCHandler.WaitForMaxServoAngleValue(ctx)
	if err != nil {
		return fmt.Errorf("failed to wait for max servo direction value: %w", err)
	}
	h.handlerLoggerProducer.Info(
		fmt.Sprintf(
			"Max servo direction value received: %d",
			maxServoAngle,
		),
	)
	h.maxServoAngleValue = maxServoAngle

	// Start the pilot
	switch challenge {
	case internal.ChallengeWithObstacles:
		h.handlerLoggerProducer.Info("Starting challenge with obstacles handler")
		return h.challengeWithObstaclesHandler(ctx)
	case internal.ChallengeWithObstaclesAndParking:
		h.handlerLoggerProducer.Info("Starting challenge with obstacles and parking handler")
		return h.challengeWithObstaclesAndParkingHandler(ctx)
	case internal.ChallengeWithoutObstacles:
		h.handlerLoggerProducer.Info("Starting challenge without obstacles handler")
		return h.challengeWithoutObstaclesHandler(ctx)
	default:
		return fmt.Errorf("unknown challenge: %s", challenge.String())
	}
}

// Run runs the pilot handler
//
// Returns:
//
// An error if the pilot could not be run, nil otherwise
func (h *DefaultHandler) Run() error {
	h.mutex.Lock()

	// Check if it's already running
	if h.IsRunning() {
		h.mutex.Unlock()
		return ErrHandlerAlreadyRunning
	}
	defer func() {
		h.mutex.Lock()

		// Set running to false
		h.isRunning.Store(false)

		h.mutex.Unlock()
	}()

	// Set running to true
	h.isRunning.Store(true)

	h.mutex.Unlock()

	// Set servo direction and motor direction to initial values
	h.servoDirection = ServoDirectionStraight
	h.motorDirection = MotorDirectionStop

	// Context canceled on SIGINT/SIGTERM.
	ctx, stop := signal.NotifyContext(
		context.Background(),
		os.Interrupt,
		syscall.SIGTERM,
	)

	// Create an error group to manage goroutines
	g := errgroup.Group{}

	// Initialize the logger goroutine
	g.Go(
		func() error {
			defer fmt.Println("Logger goroutine exited")
			return h.logger.Run(ctx, stop)
		},
	)

	// Wait a moment to ensure the logger is ready
	fmt.Println("Waiting for logger to be ready...")
	if err := h.logger.WaitUntilReady(ctx); err != nil {
		log.Fatalf("failed to wait for logger readiness: %v", err)
	}
	fmt.Println("Logger is ready")

	// Create a logger producer
	handlerLoggerProducer, err := h.logger.NewProducer(
		HandlerLoggerProducerTag,
		h.debug,
	)
	if err != nil {
		return fmt.Errorf("failed to create handler logger producer: %w", err)
	}
	h.handlerLoggerProducer = handlerLoggerProducer

	// Generate the CLIP embeddings
	h.handlerLoggerProducer.Info("Generating CLIP embeddings")
	if err = h.clipHandler.GenerateEmbeddings(ctx); err != nil {
		if errors.Is(err, gohailocliphandler.ErrEmptyGenerateEmbeddingsPath) {
			h.handlerLoggerProducer.Warning(
				fmt.Sprintf("CLIP embeddings path is empty: %v", err),
			)
		} else {
			stop()
			h.handlerLoggerProducer.Error(
				fmt.Errorf("failed to generate CLIP embeddings: %w", err),
			)
			h.handlerLoggerProducer.Info("Stopping all goroutines...")
			h.handlerLoggerProducer.Close()
			return g.Wait()
		}
	}
	h.handlerLoggerProducer.Info("CLIP embeddings generated successfully")
	defer stop()

	// Initialize the CLIP goroutine
	g.Go(
		func() error {
			defer fmt.Println("CLIP goroutine exited")
			return h.clipHandler.Run(ctx, stop)
		},
	)

	// Initialize the RPLiDAR goroutine
	g.Go(
		func() error {
			defer fmt.Println("RPLiDAR goroutine exited")
			return h.rplidarHandler.Run(ctx, stop)
		},
	)

	// Initialize the USB-CDC goroutine
	g.Go(
		func() error {
			defer fmt.Println("USB-CDC goroutine exited")
			return h.usbCDCHandler.Run(ctx, stop)
		},
	)

	// Wait USB-CDC to be ready
	h.handlerLoggerProducer.Info("Waiting for USB-CDC handler to be ready...")
	if err := h.usbCDCHandler.WaitUntilReady(ctx); err != nil {
		stop()
		h.handlerLoggerProducer.Error(
			fmt.Errorf(
				"failed to wait for USB-CDC handler readiness: %w",
				err,
			),
		)
		h.handlerLoggerProducer.Info("Stopping all goroutines...")
		h.handlerLoggerProducer.Close()
		return g.Wait()
	}
	h.handlerLoggerProducer.Info("USB-CDC handler is ready")

	// Initialize the run to wrap goroutine
	g.Go(
		func() error {
			defer func() {
				if r := recover(); r != nil {
					h.handlerLoggerProducer.Error(
						fmt.Errorf("panic recovered: %v", r),
					)
				}
				h.handlerLoggerProducer.Close()
				stop()
			}()
			
			return goconcurrentlogger.StopContextAndLogOnError(
				ctx,
				stop,
				func(ctx context.Context) error {
					return h.runToWrap(ctx)
				},
				h.handlerLoggerProducer,
			)()
		},
	)

	// Wait for the goroutines to finish
	return g.Wait()
}
