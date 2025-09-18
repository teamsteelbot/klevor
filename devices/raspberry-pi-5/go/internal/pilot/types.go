package pilot

import (
	"context"
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

const (
	// SameUpdateServoInterval is the interval to update the servo even if the direction and angle are the same
	SameUpdateServoInterval = 1 * time.Second

	// SameUpdateMotorInterval is the interval to update the motor even if the speed and direction are the same
	SameUpdateMotorInterval = 1 * time.Second

	// ChangeMotorDirectionDelay is the delay to wait before changing the motor direction
	ChangeMotorDirectionDelay = 1 * time.Second
)

type (
	// DefaultHandler is the default implementation of the Handler interface
	DefaultHandler struct {
		mutex                   sync.Mutex
		handlerLoggerProducer   goconcurrentlogger.LoggerProducer
		logger                  goconcurrentlogger.Logger
		rplidarHandler          gorplidarsdkhandler.Handler
		clipHandler             gohailocliphandler.Handler
		usbCDCHandler           internalusbcdc.Handler
		usbCDCSender            internalusbcdc.Sender
		isRunning               atomic.Bool
		servoDirection          ServoDirection
		servoAngle              uint16
		motorDirection          MotorDirection
		motorSpeed              uint16
		lastMotorSpeedUpdate    time.Time
		lastServoAngleUpdate time.Time
		rplidarMeasures         *[360]*gorplidarsdkhandler.Measure
		rplidarAverageDistances map[gorplidarsdkhandler.CardinalDirection]float64
		clipClassification      *gohailocliphandler.Classification
		latestUpdateTime        time.Time
		bno08xLastTurns         int
		rplidarTurnsCounter     int
		maxMotorSpeedValue      uint16
		maxServoDirectionValue  uint16
		debug                   bool
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
// speed: The speed to set the motor
// direction: The direction to set the motor
//
// Returns:
//
// An error if the speed could not be set, nil otherwise
func (h *DefaultHandler) setMotorSpeed(
	speed uint16,
	direction MotorDirection,
) error {
	// Update the motor direction and speed
	previousMotorDirection := h.motorDirection
	h.motorDirection = direction
	h.motorSpeed = speed

	// Check if the speed or direction is the same as the current one
	if h.motorDirection == direction && h.motorSpeed == speed {
		// Check the time that has passed since the last update, this ensures that the motor is updated at least every SameUpdateMotorInterval
		if time.Since(h.lastMotorSpeedUpdate) < SameUpdateMotorInterval {
			// No need to update the motor
			return nil
		}
	}

	// Update the last update time
	h.lastMotorSpeedUpdate = time.Now()
	
	// Send the outgoing message to set the motor speed
	if direction == MotorDirectionStop || speed == 0 {
		h.handlerLoggerProducer.Info(
			"Setting motor speed to 0, stopping the motor",
		)
		return h.usbCDCSender.SendMessage(
			internalusbcdc.OutgoingMotorSpeedStopMessage,
		)
	}

	// If the direction changed, send a stop message first
	if previousMotorDirection != direction {
		h.handlerLoggerProducer.Info(
			"Motor direction changed, stopping the motor first",
		)
		if err := h.usbCDCSender.SendMessage(	
			internalusbcdc.OutgoingMotorSpeedStopMessage,
		); err != nil {
			return fmt.Errorf("failed to stop motor before changing direction: %w", err)
		}

		// Wait a short moment to ensure the motor stops before changing direction
		time.Sleep(ChangeMotorDirectionDelay)
	}

	// Log the motor speed and direction
	if direction == MotorDirectionForward {
		h.handlerLoggerProducer.Info(
			fmt.Sprintf(
				"Setting motor speed to %d in forward direction",
				speed,
			),
		)
		return h.usbCDCSender.SendMessage(
			internalusbcdc.NewOutgoingMessageFromUint16Data(
				internalusbcdc.OutgoingCategoryMotorSpeedForward,
				speed,
			),
		)
	}
	if direction == MotorDirectionBackward {
		h.handlerLoggerProducer.Info(
			fmt.Sprintf(
				"Setting motor speed to %d in backward direction",
				speed,
			),
		)
		return h.usbCDCSender.SendMessage(
			internalusbcdc.NewOutgoingMessageFromUint16Data(
				internalusbcdc.OutgoingCategoryMotorSpeedBackward,
				speed,
			),
		)
	}
	return ErrInvalidMotorDirection
}

// setMotorSpeedByPercentage sets the motor speed by percentage of the maximum motor speed value
func (h *DefaultHandler) setMotorSpeedByPercentage(
	percentage float64,
	direction MotorDirection,
) error {
	if h.maxMotorSpeedValue == 0 {
		return ErrMaxMotorSpeedValueNotSet
	}

	speed := uint16(float64(h.maxMotorSpeedValue) * percentage)
	return h.setMotorSpeed(speed, direction)
}

// setMotorStop stops the motor
//
// Returns:
//
// An error if the motor could not be stopped, nil otherwise
func (h *DefaultHandler) setMotorStop() error {
	return h.setMotorSpeed(0, MotorDirectionStop)
}

// setMotorForwardByPercentage sets the motor speed to forward by percentage of the maximum motor speed value
//
// Parameters:
//
// percentage: The percentage of the maximum motor speed value to set the motor
//
// Returns:
//
// An error if the speed could not be set, nil otherwise
func (h *DefaultHandler) setMotorForwardByPercentage(percentage float64) error {
	return h.setMotorSpeedByPercentage(percentage, MotorDirectionForward)
}

// setMotorBackwardByPercentage sets the motor speed to backward by percentage of the maximum motor speed value
//
// Parameters:
//
// percentage: The percentage of the maximum motor speed value to set the motor
//
// Returns:
//
// An error if the speed could not be set, nil otherwise
func (h *DefaultHandler) setMotorBackwardByPercentage(percentage float64) error {
	return h.setMotorSpeedByPercentage(percentage, MotorDirectionBackward)
}

// setServoDirection sets the servo direction
//
// Parameters:
//
// angle: The angle to set the servo
// direction: The direction to set the servo
//
// Returns:
//
// An error if the servo direction could not be set, nil otherwise
func (h *DefaultHandler) setServoDirection(
	angle uint16,
	direction ServoDirection,
) error {
	// Update the servo direction and angle
	h.servoDirection = direction
	h.servoAngle = angle

	// Check if the speed or direction is the same as the current one
	if h.servoDirection == direction && h.servoAngle == angle {
		// Check the time that has passed since the last update, this ensures that the servo is updated at least every SameUpdateServoInterval
		if time.Since(h.lastServoAngleUpdate) < SameUpdateServoInterval {
			// No need to update the servo
			return nil
		}
	}

	// Update the last update time
	h.lastServoAngleUpdate = time.Now()

	// Send the outgoing message to set the angle speed
	if direction == ServoDirectionStraight || angle == 90 {
		h.handlerLoggerProducer.Info("Setting servo direction to center")
		return h.usbCDCSender.SendMessage(
			internalusbcdc.OutgoingServoDirectionCenterMessage,
		)
	}
	if direction == ServoDirectionLeft {
		h.handlerLoggerProducer.Info(
			fmt.Sprintf("Setting servo direction to left with angle %d", angle),
		)

		// Send the message
		return h.usbCDCSender.SendMessage(
			internalusbcdc.NewOutgoingMessageFromUint16Data(
				internalusbcdc.OutgoingCategoryServoDirectionToLeft,
				angle,
			),
		)
	}
	if direction == ServoDirectionRight {
		h.handlerLoggerProducer.Info(
			fmt.Sprintf(
				"Setting servo direction to right with angle %d",
				angle,
			),
		)
		return h.usbCDCSender.SendMessage(
			internalusbcdc.NewOutgoingMessageFromUint16Data(
				internalusbcdc.OutgoingCategoryServoDirectionToRight,
				angle,
			),
		)
	}
	return ErrInvalidServoDirection
}

// setServoDirectionByPercentage sets the servo direction by percentage of the maximum servo direction value
//
// Parameters:
//
// percentage: The percentage of the maximum servo direction value to set the servo
//
// Returns:
//
// An error if the servo direction could not be set, nil otherwise
func (h *DefaultHandler) setServoDirectionByPercentage(
	percentage float64,
	direction ServoDirection,
) error {
	if h.maxServoDirectionValue == 0 {
		return ErrMaxServoDirectionValueNotSet
	}

	angle := uint16(float64(h.maxServoDirectionValue) * percentage)
	return h.setServoDirection(angle, direction)
}

// setServoToCenter sets the servo to the center position
//
// Returns:
//
// An error if the servo could not be set to center, nil otherwise
func (h *DefaultHandler) setServoToCenter() error {
	return h.setServoDirection(90, ServoDirectionStraight)
}

// setServoToLeft sets the servo to the left direction
//
// Parameters:
//
// angle: The angle to set the servo
//
// Returns:
//
// An error if the servo could not be set to left, nil otherwise
func (h *DefaultHandler) setServoToLeft(angle uint16) error {
	return h.setServoDirection(angle, ServoDirectionLeft)
}

// setServoToLeftByPercentage sets the servo to the left direction by percentage of the maximum servo direction value
//
// Parameters:
//
// percentage: The percentage of the maximum servo direction value to set the servo
//
// Returns:
//
// An error if the servo could not be set to left, nil otherwise
func (h *DefaultHandler) setServoToLeftByPercentage(percentage float64) error {
	return h.setServoDirectionByPercentage(percentage, ServoDirectionLeft)
}

// setServoToRight sets the servo to the right direction
//
// Parameters:
//
// angle: The angle to set the servo
//
// Returns:
//
// An error if the servo could not be set to right, nil otherwise
func (h *DefaultHandler) setServoToRight(angle uint16) error {
	return h.setServoDirection(angle, ServoDirectionRight)
}

// setServoToRightByPercentage sets the servo to the right direction by percentage of the maximum servo direction value
//
// Parameters:
//
// percentage: The percentage of the maximum servo direction value to set the servo
//
// Returns:
//
// An error if the servo could not be set to right, nil otherwise
func (h *DefaultHandler) setServoToRightByPercentage(percentage float64) error {
	return h.setServoDirectionByPercentage(percentage, ServoDirectionRight)
}

// setServoToOppositeDirection sets the servo to the opposite direction
//
// Parameters:
//
// servoAngle: The angle to set the servo. If 0, the servo will be set to center
//
// Returns:
//
// An error if the servo could not be set to the opposite direction, nil otherwise
func (h *DefaultHandler) setServoToOppositeDirection(servoAngle uint16) error {
	// If the servo angle is 0, set it to center
	if h.servoAngle == 0 {
		return h.setServoToCenter()
	}

	// Set the servo to the opposite direction
	switch h.servoDirection {
	case ServoDirectionRight:
		return h.setServoToLeft(servoAngle)
	case ServoDirectionLeft:
		return h.setServoToRight(servoAngle)
	}
	return nil
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
	h.rplidarAverageDistances = averageDistances
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
	for {
		select {
		case <-ctx.Done():
			return ctx.Err()
		default:
			return ErrNotImplemented
		}
	}
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
	var completed bool
	var westAverageDistance, eastAverageDistance, northAverageDistance, northNortheastAverageDistance, northNorthwestAverageDistance float64
	for !completed {
		// Wait for the command delay
		time.Sleep(CommandDelay)

		select {
		case <-ctx.Done():
			return ctx.Err()
		default:
			// Update the RPLiDAR average distances
			if err := h.updateRPLiDARAverageDistances(); err != nil {
				return fmt.Errorf("failed to update RPLiDAR average distances: %w", err)
			}
			westAverageDistance = h.getAverageDirectionDistance(gorplidarsdkhandler.CardinalDirectionWest)
			eastAverageDistance = h.getAverageDirectionDistance(gorplidarsdkhandler.CardinalDirectionEast)
			northAverageDistance = h.getAverageDirectionDistance(gorplidarsdkhandler.CardinalDirectionNorth)
			northNortheastAverageDistance = h.getAverageDirectionDistance(gorplidarsdkhandler.CardinalDirectionNorthNortheast)
			northNorthwestAverageDistance = h.getAverageDirectionDistance(gorplidarsdkhandler.CardinalDirectionNorthNorthwest)

			// Log the average distances
			if h.handlerLoggerProducer.IsDebug() {
				h.handlerLoggerProducer.Debug(
					fmt.Sprintf(
						"West: %f, North-Northwest: %f, North: %f, North-Northeast: %f, East: %f",
						northAverageDistance,
						westAverageDistance,
						eastAverageDistance,
						northNortheastAverageDistance,
						northNorthwestAverageDistance,
					),
				)
			}

			// Check if one of them is 0
			if westAverageDistance == 0 || eastAverageDistance == 0 || northAverageDistance == 0 || northNortheastAverageDistance == 0 || northNorthwestAverageDistance == 0 {
				h.handlerLoggerProducer.Warning(
					"One of the average distances is 0. This may cause unexpected behavior. Waiting for new measures...",
				)
				continue
			}

			// Check if the front distance is below the safety threshold
			if northAverageDistance < SafetyFrontDistanceStartThreshold || northNortheastAverageDistance < SafetyFrontDistanceStartThreshold || northNorthwestAverageDistance < SafetyFrontDistanceStartThreshold {
				// Store the current servo angle and motor speed
				previousServoAngle := h.servoAngle
				previousMotorSpeed := h.motorSpeed

				// Log the warning
				h.handlerLoggerProducer.Warning(
					fmt.Sprintf(
						"Front distance is below the safety threshold %f.",
						SafetyFrontDistanceStartThreshold,
					),
				)

				// Set the servo to center and the motor to backward
				if err := h.setServoToCenter(); err != nil {
					return fmt.Errorf("failed to set servo to center: %w", err)
				}

				if err := h.setMotorBackwardByPercentage(MotorSlowPercentage); err != nil {
					return fmt.Errorf(
						"failed to set motor to backward: %w",
						err,
					)
				}

				var safe bool
				for !safe {
					// Wait for the command delay
					time.Sleep(CommandDelay)

					select {
					case <-ctx.Done():
						return ctx.Err()
					default:
						// Update the RPLiDAR average distances
						if err := h.updateRPLiDARAverageDistances(); err != nil {
							return fmt.Errorf("failed to update RPLiDAR average distances: %w", err)
						}
						northAverageDistance = h.getAverageDirectionDistance(gorplidarsdkhandler.CardinalDirectionNorth)
						northNortheastAverageDistance = h.getAverageDirectionDistance(gorplidarsdkhandler.CardinalDirectionNorthNortheast)
						northNorthwestAverageDistance = h.getAverageDirectionDistance(gorplidarsdkhandler.CardinalDirectionNorthNorthwest)

						if northAverageDistance >= SafetyFrontDistanceStopThreshold || northNortheastAverageDistance >= SafetyFrontDistanceStopThreshold || northNorthwestAverageDistance >= SafetyFrontDistanceStopThreshold {
							h.handlerLoggerProducer.Info("Safety front distance threshold reached.")
							safe = true
						}
					}
				}

				// Set previous servo angle and motor speed back to normal
				switch h.servoDirection {
				case ServoDirectionLeft:
					if err := h.setServoToLeft(previousServoAngle); err != nil {
						return fmt.Errorf(
							"failed to set servo to previous left angle: %w",
							err,
						)
					}
				case ServoDirectionRight:
					if err := h.setServoToRight(previousServoAngle); err != nil {
						return fmt.Errorf(
							"failed to set servo to previous right angle: %w",
							err,
						)
					}
				case ServoDirectionStraight:
					if err := h.setServoToOppositeDirection(previousServoAngle); err != nil {
						return fmt.Errorf(
							"failed to set servo to center: %w",
							err,
						)
					}
				}
				if err := h.setMotorSpeed(
					previousMotorSpeed,
					h.motorDirection,
				); err != nil {
					return fmt.Errorf(
						"failed to set motor to previous speed: %w",
						err,
					)
				}

				continue
			}

			// Check for the current turn and center the servo if necessary
			if h.servoDirection != ServoDirectionStraight {
				// Get the latest BNO08x turns value
				turns := h.usbCDCHandler.GetTurns()
				if turns > h.bno08xLastTurns {
					h.handlerLoggerProducer.Info(
						fmt.Sprintf(
							"Detected a turn. Current turns: %d, Last turns: %d",
							turns,
							h.bno08xLastTurns,
						),
					)

					// Center the servo
					if err := h.setServoToCenter(); err != nil {
						return fmt.Errorf(
							"failed to set servo to center: %w",
							err,
						)
					}

					// Update for the next check
					h.bno08xLastTurns = turns

					// Update the servo direction to straight
					h.servoDirection = ServoDirectionStraight
				} else if northAverageDistance >= FrontStopTurnDistanceThreshold {
					h.handlerLoggerProducer.Info("Front distance is safe. Stopping the turning state.")

					// Center the servo
					if err := h.setServoToCenter(); err != nil {
						return fmt.Errorf(
							"failed to set servo to center: %w",
							err,
						)
					}

					// Update the servo direction to straight
					h.servoDirection = ServoDirectionStraight
				}

				continue
			}

			// Check if it's almost time to stop
			if h.bno08xLastTurns >= AlgorithmTurns || h.rplidarTurnsCounter >= AlgorithmTurns {
				h.handlerLoggerProducer.Info("Almost time to stop. Monitoring front distance...")

				// Set the servo to center and the motor to slow speed
				if err := h.setServoToCenter(); err != nil {
					return fmt.Errorf("failed to set servo to center: %w", err)
				}
				if err := h.setMotorForwardByPercentage(MotorSlowPercentage); err != nil {
					return fmt.Errorf(
						"failed to set motor to slow speed: %w",
						err,
					)
				}

				for !completed {
					// Wait for the command delay
					time.Sleep(CommandDelay)

					select {
					case <-ctx.Done():
						return ctx.Err()
					default:
						// Update the RPLiDAR average distances
						if err := h.updateRPLiDARAverageDistances(); err != nil {
							return fmt.Errorf("failed to update RPLiDAR average distances: %w", err)
						}
						northAverageDistance = h.getAverageDirectionDistance(gorplidarsdkhandler.CardinalDirectionNorth)

						if northAverageDistance <= StopDistanceThreshold {
							completed = true
							h.handlerLoggerProducer.Info("Challenge completed successfully. Stopping the robot.")
						}
					}
				}
				continue
			}

			// Check if the robot should move forward or turn
			if northAverageDistance >= FrontStartTurnDistanceThreshold {
				var motorSpeedPercentage float64
				if northNortheastAverageDistance >= FrontStartTurnDistanceThreshold && northNorthwestAverageDistance >= FrontStartTurnDistanceThreshold {
					motorSpeedPercentage = MotorFastPercentage
				} else {
					motorSpeedPercentage = MotorNormalPercentage
				}

				// Move forward
				if err := h.setMotorForwardByPercentage(motorSpeedPercentage); err != nil {
					return fmt.Errorf(
						"failed to set motor to forward speed: %w",
						err,
					)
				}

				// Check if the servo should make a little turn to the left or right in order to center the robot
				if eastAverageDistance >= westAverageDistance*(1+SideDistanceDifferencePercentage) {
					if err := h.setServoToRightByPercentage(ServoSmallTurnAnglePercentage); err != nil {
						return fmt.Errorf(
							"failed to set servo to small right turn: %w",
							err,
						)
					}
				} else if westAverageDistance >= eastAverageDistance*(1+SideDistanceDifferencePercentage) {
					if err := h.setServoToLeftByPercentage(ServoSmallTurnAnglePercentage); err != nil {
						return fmt.Errorf(
							"failed to set servo to small left turn: %w",
							err,
						)
					}
				} else {
					if err := h.setServoToCenter(); err != nil {
						return fmt.Errorf(
							"failed to set servo to center: %w",
							err,
						)
					}
				}
				continue
			}

			if err := h.setMotorForwardByPercentage(MotorNormalPercentage); err != nil {
				return fmt.Errorf(
					"failed to set motor to normal speed: %w",
					err,
				)
			}

			// Check if the robot should turn left or right based on the side distances
			if eastAverageDistance >= SideDistanceThreshold {
				if err := h.setServoToRightByPercentage(ServoBigTurnAnglePercentage); err != nil {
					return fmt.Errorf(
						"failed to set servo to big right turn: %w",
						err,
					)
				}
				h.servoDirection = ServoDirectionRight
			} else if westAverageDistance >= SideDistanceThreshold {
				if err := h.setServoToLeftByPercentage(ServoBigTurnAnglePercentage); err != nil {
					return fmt.Errorf(
						"failed to set servo to big left turn: %w",
						err,
					)
				}
				h.servoDirection = ServoDirectionLeft
			}

			// If the robot is turning, increment the RPLiDAR turns counter
			if h.servoDirection != ServoDirectionStraight {
				h.rplidarTurnsCounter++
			}
		}
	}

	// Center the servo and stop the motor
	if err := h.setServoToCenter(); err != nil {
		return fmt.Errorf("failed to set servo to center: %w", err)
	}
	if err := h.setMotorStop(); err != nil {
		return fmt.Errorf("failed to stop the motor: %w", err)
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
	defer h.handlerLoggerProducer.Close()

	// Initialize BNO08x last turns to 0 and RPLiDAR turns counter to 0
	h.bno08xLastTurns = 0
	h.rplidarTurnsCounter = 0

	// Initialize the USB-CDC sender
	usbCDCSender, err := h.usbCDCHandler.NewSender()
	if err != nil {
		return fmt.Errorf("failed to create USB-CDC sender: %w", err)
	}
	h.usbCDCSender = usbCDCSender
	defer h.usbCDCSender.Close()

	// Wait for the challenge message to be set
	h.handlerLoggerProducer.Info("Waiting for challenge message...")
	challenge, err := h.usbCDCHandler.WaitForChallenge(ctx)
	if err != nil {
		h.handlerLoggerProducer.Error(
			fmt.Errorf("failed to wait for challenge message: %w", err),
		)
		return err
	}
	h.handlerLoggerProducer.Info(
		fmt.Sprintf("Challenge message received: %s", challenge.String()),
	)

	// Wait for max motor speed value to be set
	h.handlerLoggerProducer.Info("Waiting for max motor speed value...")
	maxMotorSpeed, err := h.usbCDCHandler.WaitForMaxMotorSpeedValue(ctx)
	if err != nil {
		h.handlerLoggerProducer.Error(
			fmt.Errorf("failed to wait for max motor speed value: %w", err),
		)
		return err
	}
	h.handlerLoggerProducer.Info(
		fmt.Sprintf("Max motor speed value received: %d", maxMotorSpeed),
	)
	h.maxMotorSpeedValue = maxMotorSpeed

	// Wait for max servo direction value to be set
	h.handlerLoggerProducer.Info("Waiting for max servo direction value...")
	maxServoDirection, err := h.usbCDCHandler.WaitForMaxServoDirectionValue(ctx)
	if err != nil {
		h.handlerLoggerProducer.Error(
			fmt.Errorf("failed to wait for max servo direction value: %w", err),
		)
		return err
	}
	h.handlerLoggerProducer.Info(
		fmt.Sprintf(
			"Max servo direction value received: %d",
			maxServoDirection,
		),
	)
	h.maxServoDirectionValue = maxServoDirection

	// Start the pilot
	var handlerFn func(context.Context) error
	switch challenge {
	case internal.ChallengeWithObstacles:
		h.handlerLoggerProducer.Info("Starting challenge with obstacles handler")
		handlerFn = h.challengeWithObstaclesHandler
	case internal.ChallengeWithObstaclesAndParking:
		h.handlerLoggerProducer.Info("Starting challenge with obstacles and parking handler")
		handlerFn = h.challengeWithObstaclesAndParkingHandler
	case internal.ChallengeWithoutObstacles:
		h.handlerLoggerProducer.Info("Starting challenge without obstacles handler")
		handlerFn = h.challengeWithoutObstaclesHandler
	}

	if handlerFn == nil {
		return fmt.Errorf("unknown challenge: %s", challenge.String())
	}
	return handlerFn(ctx)
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
		if err == gohailocliphandler.ErrEmptyGenerateEmbeddingsPath {
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
			defer fmt.Println("Pilot goroutine exited")
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
