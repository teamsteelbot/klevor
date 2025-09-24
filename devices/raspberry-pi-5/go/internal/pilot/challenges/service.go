package challenges

import (
	"context"
	"errors"
	"fmt"
	"math"
	"sync"
	"sync/atomic"
	"time"

	goconcurrentlogger "github.com/ralvarezdev/go-concurrent-logger"
	gohailocliphandler "github.com/ralvarezdev/go-hailo-clip-handler"
	gorplidarsdkhandler "github.com/ralvarezdev/go-rplidar-sdk-handler"
	"github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal"
	internalusbcdc "github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal/usbcdc"
	"golang.org/x/sync/errgroup"
)

const (
	// AverageAngleWidth is the width of the angle for average calculations
	AverageAngleWidth = 3

	// SetServoAngleAttempts is the number of attempts to set the servo angle
	SetServoAngleAttempts = 3

	// SetMotorSpeedAttempts is the number of attempts to set the motor speed
	SetMotorSpeedAttempts = 3

	// MotorSpeedStartMessageTimeout is the timeout for the motor speed start message
	MotorSpeedStartMessageTimeout = 1 * time.Second // 200ms, 500ms

	// ServoAngleStartMessageTimeout is the timeout for the servo angle start message
	ServoAngleStartMessageTimeout = 1 * time.Second

	// MotorSpeedEndMessageTimeout is the timeout for the motor speed end message
	MotorSpeedEndMessageTimeout = 3 * time.Second // 1500 ms, 2000ms

	// ServoAngleEndMessageTimeout is the timeout for the servo angle end message
	ServoAngleEndMessageTimeout = 1 * time.Second // 200 ms, 500ms

	// InitializationDelay is the delay after initialization
	InitializationDelay = 200 * time.Millisecond

	// RPLiDARLogInterval is the interval for RPLiDAR logging
	RPLiDARLogInterval = 100 * time.Millisecond

	// CLIPLogInterval is the interval for CLIP logging
	CLIPLogInterval = 100 * time.Millisecond
)

type (
	// DefaultService is the default implementation of the Service interface
	DefaultService struct {
		motorSpeed                    float64
		motorDirection                MotorDirection
		servoAngle                    float64
		servoDirection                ServoDirection
		clipHandlerMutex              sync.Mutex
		clipHandler                   gohailocliphandler.Handler
		clipClassification            *gohailocliphandler.Classification
		rplidarHandlerMutex           sync.RWMutex
		rplidarHandler                gorplidarsdkhandler.Handler
		rplidarAverageDistances       map[gorplidarsdkhandler.CardinalDirection]float64
		rplidarAverageDistancesChange map[gorplidarsdkhandler.CardinalDirection]float64
		usbCDCSender                  internalusbcdc.Sender
		usbCDCHandler                 internalusbcdc.Handler
		southSouthwestAverageDistance float64
		southSoutheastAverageDistance float64
		westAverageDistance           float64
		northwestAverageDistance      float64
		northNorthwestAverageDistance float64
		northAverageDistance          float64
		northNortheastAverageDistance float64
		northeastAverageDistance      float64
		eastAverageDistance           float64
		isRunning                     atomic.Bool
		logger                        goconcurrentlogger.Logger
		serviceLoggerProducer         goconcurrentlogger.LoggerProducer
		readyCh                       chan struct{}
		mutex                         sync.Mutex
		debug                         bool
		gyroscopeOrientation          internal.GyroscopeOrientation
	}
)

// NewDefaultService creates a new instance of DefaultService
//
// Parameters:
//
// logger: The logger to use for logging messages
// rplidarHandler: The RPLiDAR handler to use for getting distance measurements
// clipHandler: The CLIP handler to use for controlling the robot's movement
// usbCDCHandler: The USB-CDC handler to use for communication with the robot
// gyroscopeOrientation: The orientation of the gyroscope (clockwise or counter-clockwise)
// debug: A boolean indicating if debug logging is enabled
//
// Returns:
//
// A pointer to the newly created DefaultService instance, or an error if the service could not be created
func NewDefaultService(
	logger goconcurrentlogger.Logger,
	rplidarHandler gorplidarsdkhandler.Handler,
	clipHandler gohailocliphandler.Handler,
	usbCDCHandler internalusbcdc.Handler,
	gyroscopeOrientation internal.GyroscopeOrientation,
	debug bool,
) (*DefaultService, error) {
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

	return &DefaultService{
		motorSpeed:           0,
		motorDirection:       MotorDirectionStop,
		servoAngle:           0,
		servoDirection:       ServoDirectionStraight,
		clipHandler:          clipHandler,
		rplidarHandler:       rplidarHandler,
		usbCDCHandler:        usbCDCHandler,
		logger:               logger,
		debug:                debug,
		readyCh:              make(chan struct{}),
		gyroscopeOrientation: gyroscopeOrientation,
	}, nil
}

// IsRunning returns true if the service is running, false otherwise
//
// Returns:
//
// true if the service is running, false otherwise
func (s *DefaultService) IsRunning() bool {
	return s.isRunning.Load()
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
	// Signal that the CLIP classification can send through the channel
	s.serviceLoggerProducer.Info("Starting CLIP classification updates...")
	if err := s.clipHandler.StartSendingClassifications(); err != nil {
		return fmt.Errorf(
			"failed to start sending CLIP classifications: %w",
			err,
		)
	}

	// Get the classifications channel
	s.serviceLoggerProducer.Info("Getting CLIP classifications channel...")
	classificationsCh, err := s.clipHandler.GetClassificationsChannel()
	if err != nil {
		return fmt.Errorf("failed to get classifications channel: %w", err)
	}

	// Log the start of the CLIP classification updates
	s.serviceLoggerProducer.Info("CLIP classification updates started")
	var lastCLIPClassification *gohailocliphandler.Classification
	var lastLogTime time.Time
	for {
		select {
		case <-ctx.Done():
			return ctx.Err()
		case clipClassification, ok := <-classificationsCh:
			// Check if the channel is closed
			if !ok {
				return errors.New("classifications channel closed")
			}

			// Set the last classification
			lastCLIPClassification = s.clipClassification

			// Update the CLIP classification
			s.clipHandlerMutex.Lock()
			s.clipClassification = clipClassification
			s.clipHandlerMutex.Unlock()

			// Log the classification if it has changed
			if time.Since(lastLogTime) >= CLIPLogInterval {
				if lastCLIPClassification == nil && clipClassification == nil {
					// Do nothing, both are nil
				} else if lastCLIPClassification == nil && clipClassification != nil {
					s.serviceLoggerProducer.Info(
						fmt.Sprintf(
							"CLIP classification changed: %v",
							clipClassification.GetLabel(),
						),
					)
				} else if lastCLIPClassification != nil && clipClassification == nil {
					s.serviceLoggerProducer.Info("CLIP classification changed: nil")
				} else if lastCLIPClassification.GetLabel() != clipClassification.GetLabel() {
					s.serviceLoggerProducer.Info(
						fmt.Sprintf(
							"CLIP classification changed: %s",
							clipClassification.GetLabel(),
						),
					)
				}

				// Update the last log time
				lastLogTime = time.Now()
			}
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
	// Signal that the RPLiDAR can send through the channel
	s.serviceLoggerProducer.Info("Starting RPLiDAR measures updates...")
	if err := s.rplidarHandler.StartSendingMeasures(); err != nil {
		return fmt.Errorf("failed to start sending RPLiDAR measures: %w", err)
	}

	// Get the measures channel
	s.serviceLoggerProducer.Info("Getting RPLiDAR measures channel...")
	measuresCh, err := s.rplidarHandler.GetMeasuresChannel()
	if err != nil {
		return fmt.Errorf("failed to get measures channel: %w", err)
	}

	// Log the start of the RPLiDAR measures updates
	s.serviceLoggerProducer.Info("RPLiDAR measures updates started")
	var lastLogTime time.Time
	for {
		select {
		case <-ctx.Done():
			return ctx.Err()
		case measures, ok := <-measuresCh:
			// Check if the channel is closed
			if !ok {
				return errors.New("measures channel closed")
			}

			// Calculate the average north, west and east distances
			s.rplidarHandlerMutex.Lock()
			averageDistances, err := gorplidarsdkhandler.GetAverageDistanceFromAllDirections(
				measures,
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
			if s.rplidarAverageDistances == nil {
				// Initialize the average distances change map
				s.rplidarAverageDistancesChange = make(
					map[gorplidarsdkhandler.CardinalDirection]float64,
				)
			} else {
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
						s.rplidarAverageDistancesChange[direction] = math.Max(
							newDistance-oldDistance,
							-MaxDistanceChange,
						)
					} else {
						s.rplidarAverageDistancesChange[direction] = math.Min(
							newDistance-oldDistance,
							MaxDistanceChange,
						)
					}
				}
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
				s.serviceLoggerProducer.Info(
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
		}
	}
}

// Run starts the service
//
// Parameters:
//
// ctx: The context to use for running the service
// cancelFn: A function to call to cancel the context and stop the service
// challenge: The challenge to run
//
// Returns:
//
// An error if the service could not be started or if it encounters an error while running, nil otherwise
func (s *DefaultService) Run(
	ctx context.Context,
	cancelFn context.CancelFunc,
	challenge internal.Challenge,
) error {
	s.mutex.Lock()

	// Check if it's already running
	if s.IsRunning() {
		s.mutex.Unlock()
		return ErrServiceAlreadyRunning
	}
	defer s.close()

	// Set running to true
	s.isRunning.Store(true)

	s.mutex.Unlock()

	// Create a logger producer
	serviceLoggerProducer, err := s.logger.NewProducer(
		ServiceLoggerProducerTag,
		s.debug,
	)
	if err != nil {
		return fmt.Errorf("failed to create service logger producer: %w", err)
	}
	s.serviceLoggerProducer = serviceLoggerProducer
	defer s.serviceLoggerProducer.Close()

	// Create a sender for the USB-CDC handler
	usbCDCSender, err := s.usbCDCHandler.NewSender()
	if err != nil {
		return fmt.Errorf("failed to create USB-CDC sender: %w", err)
	}
	s.usbCDCSender = usbCDCSender
	defer s.usbCDCSender.Close()

	// Create a error group for the RPLiDAR measures update goroutine
	g := errgroup.Group{}

	// Initialize the RPLiDAR measures update goroutine
	g.Go(
		goconcurrentlogger.CancelContextAndLogOnError(
			ctx,
			cancelFn,
			func(ctx context.Context) error {
				return s.updateRPLiDARAverageDistances(ctx)
			},
			s.serviceLoggerProducer,
		),
	)

	// Initialize the CLIP classification update goroutine
	if challenge == internal.ChallengeWithObstacles || challenge == internal.ChallengeWithObstaclesAndParking {
		g.Go(
			goconcurrentlogger.CancelContextAndLogOnError(
				ctx,
				cancelFn,
				func(ctx context.Context) error {
					return s.updateCLIPClassification(ctx)
				},
				s.serviceLoggerProducer,
			),
		)
	}

	// Wait until the RPLiDAR and CLIP handlers are ready
	s.serviceLoggerProducer.Info("Waiting for RPLiDAR handler to be ready...")
	if err := s.rplidarHandler.WaitUntilReady(ctx); err != nil {
		return fmt.Errorf("RPLiDAR handler is not ready: %w", err)
	}
	s.serviceLoggerProducer.Info("RPLiDAR handler is ready")

	if challenge == internal.ChallengeWithObstacles || challenge == internal.ChallengeWithObstaclesAndParking {
		s.serviceLoggerProducer.Info("Waiting for CLIP handler to be ready...")
		if err := s.clipHandler.WaitUntilReady(ctx); err != nil {
			return fmt.Errorf("CLIP handler is not ready: %w", err)
		}
		s.serviceLoggerProducer.Info("CLIP handler is ready")
	}

	// Added delay after initialization
	s.serviceLoggerProducer.Info(
		fmt.Sprintf(
			"Waiting for %s after initialization...",
			InitializationDelay,
		),
	)
	time.Sleep(InitializationDelay)

	// Log that the service is ready
	s.serviceLoggerProducer.Info("Service is ready")

	// Close the ready channel to signal that the service is ready
	close(s.readyCh)

	// Wait for the goroutines to finish
	return g.Wait()
}

// close signals no more senders will send; safe to call multiple times.
func (s *DefaultService) close() {
	s.mutex.Lock()

	// Check if the handler is already closed
	if !s.IsRunning() {
		s.mutex.Unlock()
		return
	}

	// Set running to false
	s.isRunning.Store(false)

	s.mutex.Unlock()

	// Initialize the ready channel for the next run
	s.readyCh = make(chan struct{})
}

// WaitUntilReady waits until the handler is ready to accept senders or the context is done.
//
// Parameters:
//
// ctx: The context to control cancellation and timeouts.
//
// Returns:
//
// An error if the context is done before the handler is ready.
func (s *DefaultService) WaitUntilReady(ctx context.Context) error {
	select {
	case <-ctx.Done():
		return ctx.Err()
	case <-s.readyCh:
		return nil
	}
}

// GetGyroscopeOrientation returns the orientation of the gyroscope
//
// Returns:
//
// The orientation of the gyroscope
func (s *DefaultService) GetGyroscopeOrientation() internal.GyroscopeOrientation {
	return s.gyroscopeOrientation
}

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
	// Check if the USB-CDC sender is nil
	if s.usbCDCSender == nil {
		return ErrNilUSBCDCSender
	}

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
			s.serviceLoggerProducer.Info(
				"Setting motor speed to 0, stopping the motor",
			)
			if err := s.usbCDCSender.SendMessage(
				internalusbcdc.OutgoingMotorSpeedStopMessage,
			); err != nil {
				return err
			}
		case MotorDirectionForward:
			s.serviceLoggerProducer.Info(
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
			s.serviceLoggerProducer.Info(
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
	ctx, cancel := context.WithTimeout(ctx, MotorSpeedEndMessageTimeout)
	defer cancel()

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

// SetServoAngle sets the servo direction
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
func (s *DefaultService) SetServoAngle(
	ctx context.Context,
	angle float64,
	direction ServoDirection,
) error {
	// Check if the USB-CDC sender is nil
	if s.usbCDCSender == nil {
		return ErrNilUSBCDCSender
	}

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
			s.serviceLoggerProducer.Info("Setting servo direction to center")
			if err := s.usbCDCSender.SendMessage(
				internalusbcdc.OutgoingServoAngleCenterMessage,
			); err != nil {
				return err
			}
		case ServoDirectionLeft:
			s.serviceLoggerProducer.Info(
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
			s.serviceLoggerProducer.Info(
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
	ctx, cancel := context.WithTimeout(ctx, ServoAngleEndMessageTimeout)
	defer cancel()

	// Wait for the servo angle end message
	if err := s.usbCDCHandler.WaitServoAngleEndMessage(ctx); err != nil && !errors.Is(
		err,
		context.DeadlineExceeded,
	) {
		return err
	}
	return nil
}

// SetServoToCenter sets the servo to the center position
//
// Parameters:
//
// ctx: The context to use for setting the servo angle
//
// Returns:
//
// An error if the servo could not be set to center, nil otherwise
func (s *DefaultService) SetServoToCenter(ctx context.Context) error {
	if err := s.SetServoAngle(ctx, 90, ServoDirectionStraight); err != nil {
		return fmt.Errorf("failed to set servo to center: %w", err)
	}
	return nil
}

// SetServoToLeft sets the servo to the left direction
//
// Parameters:
//
// ctx: The context to use for setting the servo angle
// angle: The angle to set the servo
//
// Returns:
//
// An error if the servo could not be set to left, nil otherwise
func (s *DefaultService) SetServoToLeft(
	ctx context.Context,
	angle float64,
) error {
	if err := s.SetServoAngle(ctx, angle, ServoDirectionLeft); err != nil {
		return fmt.Errorf("failed to set servo to left: %w", err)
	}
	return nil
}

// SetServoToRight sets the servo to the right direction
//
// Parameters:
//
// ctx: The context to use for setting the servo angle
// angle: The angle to set the servo
//
// Returns:
//
// An error if the servo could not be set to right, nil otherwise
func (s *DefaultService) SetServoToRight(
	ctx context.Context,
	angle float64,
) error {
	if err := s.SetServoAngle(ctx, angle, ServoDirectionRight); err != nil {
		return fmt.Errorf("failed to set servo to right: %w", err)
	}
	return nil
}

// SetServoToOppositeDirection sets the servo to the opposite direction
//
// Parameters:
//
// ctx: The context to use for setting the servo angle
// angle: The angle to set the servo. If 0, the servo will be set to center
//
// Returns:
//
// An error if the servo could not be set to the opposite direction, nil otherwise
func (s *DefaultService) SetServoToOppositeDirection(
	ctx context.Context,
	angle float64,
) error {
	switch s.servoDirection {
	case ServoDirectionRight:
		return s.SetServoToLeft(ctx, angle)
	case ServoDirectionLeft:
		return s.SetServoToRight(ctx, angle)
	case ServoDirectionStraight:
		return s.SetServoToCenter(ctx)
	default:
		return ErrInvalidServoDirection
	}
}

// GetRPLiDARAverageDistance gets the average distance for a specific direction
//
// Parameters:
//
// direction: The direction to get the average distance for
//
// Returns:
//
// The average distance for the specified direction, or 0.0 if the direction is not found
func (s *DefaultService) GetRPLiDARAverageDistance(
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

// GetRPLiDARAverageDistanceChange gets the average distance change for a specific direction
//
// Parameters:
//
// direction: The direction to get the average distance change for
//
// Returns:
//
// The average distance change for the specified direction, or 0.0 if the direction is not found
func (s *DefaultService) GetRPLiDARAverageDistanceChange(
	direction gorplidarsdkhandler.CardinalDirection,
) float64 {
	s.rplidarHandlerMutex.RLock()
	defer s.rplidarHandlerMutex.RUnlock()

	// Check if the average distances change map is nil
	if s.rplidarAverageDistancesChange == nil {
		return 0.0
	}

	// Get the average distance change for the specified direction
	distanceChange, ok := s.rplidarAverageDistancesChange[direction]
	if !ok {
		return 0.0
	}
	return distanceChange
}

// GetSouthSouthwestAverageDistance returns the average distance to the south-southwest
//
// Returns:
//
// The average distance to the south-southwest
func (s *DefaultService) GetSouthSouthwestAverageDistance() float64 {
	return s.southSouthwestAverageDistance
}

// GetSouthSoutheastAverageDistance returns the average distance to the south-southeast
//
// Returns:
//
// The average distance to the south-southeast
func (s *DefaultService) GetSouthSoutheastAverageDistance() float64 {
	return s.southSoutheastAverageDistance
}

// GetWestAverageDistance returns the average distance to the west
//
// Returns:
//
// The average distance to the west
func (s *DefaultService) GetWestAverageDistance() float64 {
	return s.westAverageDistance
}

// GetEastAverageDistance returns the average distance to the east
//
// Returns:
//
// The average distance to the east
func (s *DefaultService) GetEastAverageDistance() float64 {
	return s.eastAverageDistance
}

// GetNorthwestAverageDistance returns the average distance to the northwest
//
// Returns:
//
// The average distance to the northwest
func (s *DefaultService) GetNorthwestAverageDistance() float64 {
	return s.northwestAverageDistance
}

// GetNortheastAverageDistance returns the average distance to the northeast
//
// Returns:
//
// The average distance to the northeast
func (s *DefaultService) GetNortheastAverageDistance() float64 {
	return s.northeastAverageDistance
}

// GetNorthAverageDistance returns the average distance to the north
//
// Returns:
//
// The average distance to the north
func (s *DefaultService) GetNorthAverageDistance() float64 {
	return s.northAverageDistance
}

// Get360DegreeTurns returns the number of 360 degree turns made by the robot
//
// Returns:
//
// The number of 360 degree turns made by the robot
func (s *DefaultService) Get360DegreeTurns() int {
	return s.usbCDCHandler.Get360DegreeTurns()
}

// Get90DegreeTurns returns the number of 90 degree turns made by the robot
//
// Returns:
//
// The number of 90 degree turns made by the robot
func (s *DefaultService) Get90DegreeTurns() int {
	return s.usbCDCHandler.Get90DegreeTurns()
}

// Get45DegreeTurns returns the number of 45 degree turns made by the robot
//
// Returns:
//
// The number of 45 degree turns made by the robot
func (s *DefaultService) Get45DegreeTurns() int {
	return s.usbCDCHandler.Get45DegreeTurns()
}

// Get30DegreeTurns returns the number of 30 degree turns made by the robot
//
// Returns:
//
// The number of 30 degree turns made by the robot
func (s *DefaultService) Get30DegreeTurns() int {
	return s.usbCDCHandler.Get30DegreeTurns()
}

// GetAccumulatedYawDegrees returns the accumulated yaw degrees of the robot
//
// Returns:
//
// The accumulated yaw degrees of the robot
func (s *DefaultService) GetAccumulatedYawDegrees() float64 {
	return s.usbCDCHandler.GetAccumulatedYawDegrees()
}

// GetCLIPClassification returns the current CLIP classification
//
// Returns:
//
// A pointer to the current CLIP classification, or nil if no classification is available
func (s *DefaultService) GetCLIPClassification() *gohailocliphandler.Classification {
	s.clipHandlerMutex.Lock()
	defer s.clipHandlerMutex.Unlock()
	return s.clipClassification
}
