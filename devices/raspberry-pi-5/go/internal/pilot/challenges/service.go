package challenges

import (
	"context"
	"errors"
	"fmt"
	"math"
	"time"
	"sync"

	goconcurrentlogger "github.com/ralvarezdev/go-concurrent-logger"
	gohailocliphandler "github.com/ralvarezdev/go-hailo-clip-handler"
	gorplidarsdkhandler "github.com/ralvarezdev/go-rplidar-sdk-handler"
	internalusbcdc "github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal/usbcdc"
)

type (
	// DefaultService is the default implementation of the Service interface
	DefaultService struct {
		motorSpeed     float64
		motorDirection MotorDirection
		servoAngle     float64
		servoDirection ServoDirection
		clipHandlerMutex sync.Mutex
		clipHandler      gohailocliphandler.Handler
		clipClassification *gohailocliphandler.Classification
		rplidarHandlerMutex sync.RWMutex
		rplidarHandler      gorplidarsdkhandler.Handler
		rplidarAverageDistances       map[gorplidarsdkhandler.CardinalDirection]float64
		rplidarAverageDistancesChange map[gorplidarsdkhandler.CardinalDirection]float64
		usbCDCSender   internalusbcdc.Sender
		usbCDCHandler  internalusbcdc.Handler
		southSouthwestAverageDistance float64
		southSoutheastAverageDistance float64
		westAverageDistance           float64
		northwestAverageDistance      float64
		northNorthwestAverageDistance float64
		northAverageDistance          float64
		northNortheastAverageDistance float64
		northeastAverageDistance      float64
		eastAverageDistance           float64
		logger goconcurrentlogger.Logger
		handlerLoggerProducer goconcurrentlogger.LoggerProducer
		readyCh chan struct{}
	}
)

// GetMotorSpeed returns the current motor speed
//
// Returns:
//
// The current motor speed
func (s *DefaultService) GetMotorSpeed() float64 {
	return s.motorSpeed
}

// GetMotorDirection returns the current motor direction
//
// Returns:
//
// The current motor direction
func (s *DefaultService) GetMotorDirection() MotorDirection {
	return s.motorDirection
}

// GetServoAngle returns the current servo angle
//
// Returns:
//
// The current servo angle
func (s *DefaultService) GetServoAngle() float64 {
	return s.servoAngle
}

// GetServoDirection returns the current servo direction
//
// Returns:
//
// The current servo direction
func (s *DefaultService) GetServoDirection() ServoDirection {
	return s.servoDirection
}	

// SetMotorSpeed sets the speed of the motor
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
func (s *DefaultService) SetMotorSpeed(
	ctx context.Context,
	speed float64,
	direction MotorDirection,
) error {
	// Check if it's the same speed and direction as the current one
	if s.motorDirection == direction && s.motorSpeed == speed {
		return nil
	}

	// Clear motor speed start and end messages channel
	s.usbCDCHandler.ClearMotorSpeedStartAndEndMessagesCh()

	// Update the motor direction and speed
	s.motorDirection = direction
	s.motorSpeed = speed

	// Send the outgoing message to set the motor speed
	var receivedStartMessage bool
	for range SetMotorSpeedAttempts {
		switch direction {
		case MotorDirectionStop:
			// Log the motor stop action
			s.handlerLoggerProducer.Info(
				"Setting motor speed to 0, stopping the motor",
			)
			if err := s.usbCDCSender.SendMessage(
				internalusbcdc.OutgoingMotorSpeedStopMessage,
			); err != nil {
				return err
			}
		case MotorDirectionForward:
			s.handlerLoggerProducer.Info(
				fmt.Sprintf(
					"Setting motor speed to %.3f%% in forward direction",
					speed*100,
				),
			)
			if err := s.usbCDCSender.SendMessage(
				internalusbcdc.NewOutgoingMessageFromFloat64Data(
					internalusbcdc.OutgoingCategoryMotorSpeedForward,
					speed,
				),
			); err != nil {
				return err
			}
		case MotorDirectionBackward:
			s.handlerLoggerProducer.Info(
				fmt.Sprintf(
					"Setting motor speed to %.3f%% in backward direction",
					speed*100,
				),
			)
			if err := s.usbCDCSender.SendMessage(
				internalusbcdc.NewOutgoingMessageFromFloat64Data(
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
		if err := s.usbCDCHandler.WaitMotorSpeedStartMessage(ctx); err != nil {
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
	if err := s.usbCDCHandler.WaitMotorSpeedEndMessage(ctx); err != nil && !errors.Is(
		err,
		context.DeadlineExceeded,
	) {
		return err
	}
	return nil
}

// SetMotorStop stops the motor
//
// Parameters:
//
// ctx: The context to use for setting the motor speed
//
// Returns:
//
// An error if the motor could not be stopped, nil otherwise
func (s *DefaultService) SetMotorStop(ctx context.Context) error {
	if err := s.SetMotorSpeed(ctx, 0, MotorDirectionStop); err != nil {
		return fmt.Errorf("failed to stop motor: %w", err)
	}
	return nil
}

// SetMotorForward sets the motor speed to forward
//
// Parameters:
//
// ctx: The context to use for setting the motor speed
// speed: The speed value to set the motor
//
// Returns:
//
// An error if the speed could not be set, nil otherwise
func (s *DefaultService) SetMotorForward(
	ctx context.Context,
	speed float64,
) error {
	if err := s.SetMotorSpeed(ctx, speed, MotorDirectionForward); err != nil {
		return fmt.Errorf("failed to set motor to forward: %w", err)
	}
	return nil
}

// SetMotorBackward sets the motor speed to backward
//
// Parameters:
//
// ctx: The context to use for setting the motor speed
// speed: The motor speed value to set the motor
//
// Returns:
//
// An error if the speed could not be set, nil otherwise
func (s *DefaultService) SetMotorBackward(
	ctx context.Context,
	speed float64,
) error {
	if err := s.SetMotorSpeed(ctx, speed, MotorDirectionBackward); err != nil {
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
func (s *DefaultService) setServoAngle(
	ctx context.Context,
	angle float64,
	direction ServoDirection,
) error {
	// Check if the servo direction and angle is the same as the current one
	if s.servoDirection == direction && s.servoAngle == angle {
		return nil
	}

	// Clear servo angle start and end messages channel
	s.usbCDCHandler.ClearServoAngleStartAndEndMessagesCh()

	// Update the servo direction and angle
	s.servoDirection = direction
	s.servoAngle = angle

	// Send the outgoing message to set the angle speed
	var receivedStartMessage bool
	for range SetServoAngleAttempts {
		switch direction {
		case ServoDirectionStraight:
			s.handlerLoggerProducer.Info("Setting servo direction to center")
			if err := s.usbCDCSender.SendMessage(
				internalusbcdc.OutgoingServoAngleCenterMessage,
			); err != nil {
				return err
			}
		case ServoDirectionLeft:
			s.handlerLoggerProducer.Info(
				fmt.Sprintf(
					"Setting servo direction to left by %.3f%%",
					angle*100,
				),
			)
			if err := s.usbCDCSender.SendMessage(
				internalusbcdc.NewOutgoingMessageFromFloat64Data(
					internalusbcdc.OutgoingCategoryServoAngleToLeft,
					angle*100,
				),
			); err != nil {
				return err
			}
		case ServoDirectionRight:
			s.handlerLoggerProducer.Info(
				fmt.Sprintf(
					"Setting servo direction to right by %.3f%%",
					angle*100,
				),
			)
			if err := s.usbCDCSender.SendMessage(
				internalusbcdc.NewOutgoingMessageFromFloat64Data(
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
		if err := s.usbCDCHandler.WaitServoAngleStartMessage(ctx); err != nil {
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
	if err := s.usbCDCHandler.WaitServoAngleEndMessage(ctx); err != nil && !errors.Is(
		err,
		context.DeadlineExceeded,
	) {
		return err
	}
	return nil
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
func (s *DefaultService) setServoToCenter(ctx context.Context) error {
	if err := s.setServoAngle(ctx, 90, ServoDirectionStraight); err != nil {
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
func (s *DefaultService) setServoToLeft(
	ctx context.Context,
	angle float64,
) error {
	if err := s.setServoAngle(ctx, angle, ServoDirectionLeft); err != nil {
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
func (s *DefaultService) setServoToRight(
	ctx context.Context,
	angle float64,
) error {
	if err := s.setServoAngle(ctx, angle, ServoDirectionRight); err != nil {
		return fmt.Errorf("failed to set servo to right: %w", err)
	}
	return nil
}

// setServoToOppositeDirection sets the servo to the opposite direction
//
// Parameters:
//
// ctx: The context to use for setting the servo angle
// angle: The angle to set the servo. If 0, the servo will be set to center
//
// Returns:
//
// An error if the servo could not be set to the opposite direction, nil otherwise
func (s *DefaultService) setServoToOppositeDirection(
	ctx context.Context,
	angle float64,
) error {
	switch s.servoDirection {
	case ServoDirectionRight:
		return s.setServoToLeft(ctx, angle)
	case ServoDirectionLeft:
		return s.setServoToRight(ctx, angle)
	case ServoDirectionStraight:
		return s.setServoToCenter(ctx)
	default:
		return ErrInvalidServoDirection
	}
}

// updateCLIPClassification retrieves the latest CLIP classification
//
// Parameters:
//
// ctx: The context to use for updating the classification
//
// Returns:
//
// An error if the classification could not be retrieved
func (s *DefaultService) updateCLIPClassification(ctx context.Context) error {
	var lastCLIPClassification *gohailocliphandler.Classification
	var lastLogTime time.Time
	for {
		select {
		case <-ctx.Done():
			return ctx.Err()
		default:
			// Set the last classification
			lastCLIPClassification = s.clipClassification

			// Update the CLIP classification
			s.clipHandlerMutex.Lock()
			clipClassification, err := s.clipHandler.GetClassification()
			if err != nil {
				s.clipHandlerMutex.Unlock()
				return fmt.Errorf("failed to get CLIP classification: %w", err)
			}

			// Set the classification and unlock the mutex
			s.clipClassification = clipClassification
			s.clipHandlerMutex.Unlock()

			// Log the classification if it has changed
			if time.Since(lastLogTime) >= CLIPLogInterval {
				if lastCLIPClassification == nil && clipClassification == nil {
					// Do nothing, both are nil
				} else if lastCLIPClassification == nil && clipClassification != nil {
					s.handlerLoggerProducer.Info(
						fmt.Sprintf(
							"CLIP classification changed: %v",
							clipClassification.GetLabel(),
						),
					)
				} else if lastCLIPClassification != nil && clipClassification == nil {
					s.handlerLoggerProducer.Info("CLIP classification changed: nil")
				} else if lastCLIPClassification.GetLabel() != clipClassification.GetLabel() {
					s.handlerLoggerProducer.Info(
						fmt.Sprintf(
							"CLIP classification changed: %s",
							clipClassification.GetLabel(),
						),
					)
				}

				// Update the last log time
				lastLogTime = time.Now()
			}

			// Sleep the update delay
			time.Sleep(UpdateDelay)
		}
	}
}

// updateRPLiDARAverageDistances updates the average distances from the RPLiDAR measures
//
// Parameters:
//
// ctx: The context to use for updating the average distances
//
// Returns:
//
// An error if the average distances could not be updated, nil otherwise
func (s *DefaultService) updateRPLiDARAverageDistances(ctx context.Context) error {
	var lastLogTime time.Time
	for {
		select {
		case <-ctx.Done():
			return ctx.Err()
		default:
			// Calculate the average north, west and east distances
			s.rplidarHandlerMutex.Lock()
			averageDistances, err := s.rplidarHandler.GetAverageDistancesFromAllDirections(
				AverageAngleWidth,
			)
			if err != nil {
				s.rplidarHandlerMutex.Unlock()
				return fmt.Errorf(
					"average distances could not be calculated: %w",
					err,
				)
			}

			// Check if the handler current average distances is not nil
			if s.rplidarAverageDistances != nil {
				// Calculate the change for each direction
				for direction, newDistance := range averageDistances {
					oldDistance, ok := s.rplidarAverageDistances[direction]
					if !ok || oldDistance == 0 {
						s.rplidarAverageDistancesChange[direction] = 0.0
						continue
					}

					// Ignore if there is no change. May happen if it hasn't been updated yet
					if newDistance == oldDistance {
						continue
					}

					// Set the distance change with a maximum limit
					if newDistance < oldDistance {
						s.rplidarAverageDistancesChange[direction] = math.Max(newDistance-oldDistance, -MaxDistanceChange)
					} else {
						s.rplidarAverageDistancesChange[direction] = math.Min(newDistance - oldDistance, MaxDistanceChange)
					}
				}
			} else {
				// Initialize the average distances change map
				s.rplidarAverageDistancesChange = make(
					map[gorplidarsdkhandler.CardinalDirection]float64,
				)
			}

			// Set the average distances and the last update time
			s.rplidarAverageDistances = averageDistances

			// Get the average common distances
			s.southSoutheastAverageDistance = s.rplidarAverageDistances[gorplidarsdkhandler.CardinalDirectionSouthSoutheast]
			s.southSouthwestAverageDistance = s.rplidarAverageDistances[gorplidarsdkhandler.CardinalDirectionSouthSouthwest]
			s.westAverageDistance = s.rplidarAverageDistances[gorplidarsdkhandler.CardinalDirectionWest]
			s.northwestAverageDistance = s.rplidarAverageDistances[gorplidarsdkhandler.CardinalDirectionNorthwest]
			s.northNorthwestAverageDistance = s.rplidarAverageDistances[gorplidarsdkhandler.CardinalDirectionNorthNorthwest]
			s.northAverageDistance = s.rplidarAverageDistances[gorplidarsdkhandler.CardinalDirectionNorth]
			s.northNortheastAverageDistance = s.rplidarAverageDistances[gorplidarsdkhandler.CardinalDirectionNorthNortheast]
			s.northeastAverageDistance = s.rplidarAverageDistances[gorplidarsdkhandler.CardinalDirectionNortheast]
			s.eastAverageDistance = s.rplidarAverageDistances[gorplidarsdkhandler.CardinalDirectionEast]
			s.rplidarHandlerMutex.Unlock()

			// Log the average distances
			if time.Since(lastLogTime) >= RPLiDARLogInterval {
				s.handlerLoggerProducer.Info(
					fmt.Sprintf(
						"W: %f, NW: %f, N-NW: %f, N: %f, N-NE: %f, NE: %f, E: %f",
						s.westAverageDistance,
						s.northwestAverageDistance,
						s.northNorthwestAverageDistance,
						s.northAverageDistance,
						s.northNortheastAverageDistance,
						s.northeastAverageDistance,
						s.eastAverageDistance,
					),
				)

				// Update the last log time
				lastLogTime = time.Now()
			}

			// Sleep the update delay
			time.Sleep(UpdateDelay)
		}
	}
}

// getRPLiDARAverageDistance gets the average distance for a specific direction
//
// Parameters:
//
// direction: The direction to get the average distance for
//
// Returns:
//
// The average distance for the specified direction, or 0.0 if the direction is not found
func (s *DefaultService) getRPLiDARAverageDistance(
	direction gorplidarsdkhandler.CardinalDirection,
) float64 {
	s.rplidarHandlerMutex.RLock()
	defer s.rplidarHandlerMutex.RUnlock()

	// Check if the average distances map is nil
	if s.rplidarAverageDistances == nil {
		return 0.0
	}

	// Get the average distance for the specified direction
	distance, ok := s.rplidarAverageDistances[direction]
	if !ok {
		return 0.0
	}
	return distance
}
