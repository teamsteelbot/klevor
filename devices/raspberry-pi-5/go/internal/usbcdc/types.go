package usbcdc

import (
	"context"
	"encoding/binary"
	"fmt"
	"math"
	"sync"
	"sync/atomic"
	"time"

	goconcurrentlogger "github.com/ralvarezdev/go-concurrent-logger"
	gorplidarsdkhandler "github.com/ralvarezdev/go-rplidar-sdk-handler"
	"github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal"
	tinygoerrors "github.com/ralvarezdev/tinygo-errors"
	"go.bug.st/serial"
	"golang.org/x/sync/errgroup"
)

type (
	// YawDegreesHandler is the structure that holds the yaw degrees information.
	YawDegreesHandler struct {
		lastYawDegrees        float64
		accumulatedYawDegrees float64
	}

	// DefaultSender is the default implementation of the Sender interface
	DefaultSender struct {
		sendFn  func(*OutgoingMessage)
		closeFn func()
		mutex   sync.Mutex
		closed  atomic.Bool
	}

	// DefaultHandler is the default implementation of the Handler interface
	DefaultHandler struct {
		outgoingMessagesCh             chan *OutgoingMessage
		readyCh                        chan struct{}
		logger                         goconcurrentlogger.Logger
		handlerLoggerProducer          goconcurrentlogger.LoggerProducer
		incomingMessagesLoggerProducer goconcurrentlogger.LoggerProducer
		outgoingMessagesLoggerProducer goconcurrentlogger.LoggerProducer
		isRunning                      atomic.Bool
		closed                         atomic.Bool
		mutex                          sync.Mutex
		wgSenders                      sync.WaitGroup
		baudRate                       int
		buffer                         []byte
		accumulatedBuffer              []byte
		receivedStartMessage           bool
		receivedChallenge              internal.Challenge
		receivedBNO08XQuaternionX      float64
		receivedBNO08XQuaternionY      float64
		receivedBNO08XQuaternionZ      float64
		receivedBNO08XQuaternionW      float64
		receivedBNO08XYawDegrees       float64
		receivedBNO08XPitchDegrees     float64
		receivedBNO08XRollDegrees      float64
		yawDegreesHandler              *YawDegreesHandler
		challengeReadyCh               chan struct{}
		notifyChallengeOnce            sync.Once
		motorSpeedStartMessagesCh      chan struct{}
		motorSpeedEndMessagesCh        chan struct{}
		servoAngleStartMessagesCh      chan struct{}
		servoAngleEndMessagesCh        chan struct{}
		debug                          bool
		hasStarted                     atomic.Bool
	}
)

// NewYawDegreesHandler creates a new YawDegreesHandler instance.
//
// Parameters:
//
// initialYawDegrees: The initial yaw in degrees.
//
// Returns:
//
// A pointer to a YawDegreesHandler instance.
func NewYawDegreesHandler(initialYawDegrees float64) *YawDegreesHandler {
	return &YawDegreesHandler{
		lastYawDegrees:        initialYawDegrees,
		accumulatedYawDegrees: 0,
	}
}

// Update updates based on the new yaw degrees value.
//
// Parameters:
//
// yawDegrees: The current yaw angle in degrees
func (y *YawDegreesHandler) Update(yawDegrees float64) {
	// Calculate the change since last update
	deltaYawDegrees := yawDegrees - y.lastYawDegrees
	if deltaYawDegrees > 180 {
		deltaYawDegrees -= 360
	} else if deltaYawDegrees < -180 {
		deltaYawDegrees += 360
	}

	// Update accumulated yaw and last yaw degrees
	y.accumulatedYawDegrees += deltaYawDegrees
	y.lastYawDegrees = yawDegrees
}

//

// getNDegreeTurns returns the total number of n-degrees turns
//
// Parameters:
//
// n: The degree of turns to calculate (e.g., 90 for 90-degree turns)
//
// Returns:
//
// The total number of n-degree turns made.
func (y *YawDegreesHandler) getNDegreeTurns(n float64) float64 {
	if n == 0 {
		return 0
	}
	return math.Abs(y.accumulatedYawDegrees / n)
}

// Get360DegreeTurns returns the total number of 360-degree turns made.
//
// Returns:
//
// The total number of 360-degree turns made.
func (y *YawDegreesHandler) Get360DegreeTurns() uint {
	return uint(y.getNDegreeTurns(360))
}

// Get90DegreeTurns returns the total number of 90-degree turns made.
//
// Returns:
//
// The total number of 90-degree turns made.
func (y *YawDegreesHandler) Get90DegreeTurns() uint {
	return uint(y.getNDegreeTurns(90))
}

// Get45DegreeTurns returns the total number of 45-degree turns made.
//
// Returns:
//
// The total number of 45-degree turns made.
func (y *YawDegreesHandler) Get45DegreeTurns() uint {
	return uint(y.getNDegreeTurns(45))
}

// Get30DegreeTurns returns the total number of 30-degree turns made.
//
// Returns:
//
// The total number of 30-degree turns made.
func (y *YawDegreesHandler) Get30DegreeTurns() uint {
	return uint(y.getNDegreeTurns(30))
}

// GetAccumulatedYawDegrees returns the accumulated yaw in degrees.
//
// Returns:
//
// The accumulated yaw in degrees.
func (y *YawDegreesHandler) GetAccumulatedYawDegrees() float64 {
	return y.accumulatedYawDegrees
}

// NewDefaultSender creates a new DefaultSender instance.
//
// Parameters:
//
// sendFn: Function to send messages.
// closeFn: Function to call when done.
//
// Returns:
//
// A pointer to a DefaultSender instance or an error if the parameters are invalid.
func NewDefaultSender(
	sendFn func(*OutgoingMessage),
	closeFn func(),
) (*DefaultSender, error) {
	// Check if the sendFn is nil
	if sendFn == nil {
		return nil, ErrNilSendFunction
	}

	// Check if the closeFn is nil
	if closeFn == nil {
		return nil, ErrNilCloseFunction
	}

	// Create a new DefaultSender instance
	sender := &DefaultSender{
		sendFn:  sendFn,
		closeFn: closeFn,
	}

	return sender, nil
}

// SendMessage sends an outgoing message through USB CDC.
//
// Parameters:
//
// message: Pointer to the OutgoingMessage to be sent.
//
// Returns:
//
// An error if the message could not be sent.
func (s *DefaultSender) SendMessage(message *OutgoingMessage) error {
	// Check if the sender is closed
	if s.IsClosed() {
		return ErrSenderAlreadyClosed
	}

	// Send the message using the send function
	s.sendFn(message)
	return nil
}

// SendOKMessage sends an OK message through USB CDC.
func (s *DefaultSender) SendOKMessage() error {
	return s.SendMessage(OutgoingOKMessage)
}

// Close signals that the sender is done and performs cleanup.
func (s *DefaultSender) Close() {
	s.mutex.Lock()

	// Check if already closed to prevent multiple calls
	if s.IsClosed() {
		s.mutex.Unlock()
		return
	}

	// Mark the sender as closed
	s.closed.Store(true)

	s.mutex.Unlock()

	// Call the close function to signal completion
	s.closeFn()
}

// IsClosed returns true if the sender is closed.
//
// Returns:
//
// True if the sender is closed, false otherwise.
func (s *DefaultSender) IsClosed() bool {
	return s.closed.Load()
}

// NewDefaultHandler creates a new DefaultHandler instance
//
// Parameters:
//
// baudRate: Baud rate for the serial communication.
// logger: Logger instance for logging messages.
// debug: A boolean indicating if debug logging is enabled
//
// Returns:
//
// A pointer to a DefaultHandler instance
func NewDefaultHandler(
	baudRate int,
	logger goconcurrentlogger.Logger,
	debug bool,
) (*DefaultHandler, error) {
	// Check if the logger is nil
	if logger == nil {
		return nil, goconcurrentlogger.ErrNilLogger
	}

	// Create a buffer for reading data
	buffer := make([]byte, BufferSize)

	// Create an accumulated buffer for storing data
	accumulatedBuffer := make([]byte, 0)

	return &DefaultHandler{
		baudRate:          baudRate,
		buffer:            buffer,
		accumulatedBuffer: accumulatedBuffer,
		logger:            logger,
		readyCh:           make(chan struct{}),
		debug:             debug,
	}, nil
}

// IsRunning returns true if the handler is running
//
// Returns:
//
// True if the handler is running, false otherwise
func (h *DefaultHandler) IsRunning() bool {
	return h.isRunning.Load()
}

// runToWrap is the internal function to start the handler to read from and write to the serial port.
//
// Parameters:
//
// ctx: The context to control the lifecycle of the handler.
// cancelFn: Function to call to cancel the context.
//
// Returns:
//
// An error if any issue occurs during reading or writing.
func (h *DefaultHandler) runToWrap(ctx context.Context, cancelFn context.CancelFunc) error {
	// Create a logger producers
	incomingMessagesLoggerProducer, err := h.logger.NewProducer(
		IncomingMessagesLoggerProducerTag,
		h.debug,
	)
	if err != nil {
		return fmt.Errorf(
			"failed to create incoming messages logger producer: %w",
			err,
		)
	}
	h.incomingMessagesLoggerProducer = incomingMessagesLoggerProducer
	defer h.incomingMessagesLoggerProducer.Close()

	outgoingMessagesLoggerProducer, err := h.logger.NewProducer(
		OutgoingMessagesLoggerProducerTag,
		h.debug,
	)
	if err != nil {
		return fmt.Errorf(
			"failed to create outgoing messages logger producer: %w",
			err,
		)
	}
	h.outgoingMessagesLoggerProducer = outgoingMessagesLoggerProducer
	defer h.outgoingMessagesLoggerProducer.Close()

	// List available serial ports
	ports, err := serial.GetPortsList()
	if err != nil {
		return ErrFailedToListPorts
	}
	if len(ports) == 0 {
		return ErrNoPortsFound
	}

	// Get the only port that is different from the RPLiDAR port
	var portName string
	for _, p := range ports {
		if p != gorplidarsdkhandler.LinuxSlamtecC1Port {
			portName = p
			break
		}
	}

	// Check if the given port was found
	if portName == "" {
		return ErrPortNotFound
	}

	// Open the serial port
	mode := &serial.Mode{
		BaudRate: h.baudRate,
	}
	port, err := serial.Open(portName, mode)
	if err != nil {
		return err
	}
	defer func(port serial.Port) {
		if err := port.Close(); err != nil {
			fmt.Printf("Error closing port: %v\n", err)
		}
	}(port)

	// Set a timeout to prevent blocking forever
	if err = port.SetReadTimeout(ReadTimeout); err != nil {
		return err
	}

	// Create an error group to manage goroutines
	g := errgroup.Group{}

	// Call the incoming messages handler
	g.Go(
		goconcurrentlogger.CancelContextAndLogOnError(
			ctx,
			cancelFn,
			func(ctx context.Context) error {
				return h.incomingMessagesHandler(ctx, port)
			},
			h.incomingMessagesLoggerProducer,
		),
	)

	// Call the outgoing messages handler
	g.Go(
		goconcurrentlogger.CancelContextAndLogOnError(
			ctx,
			cancelFn,
			func(ctx context.Context) error {
				return h.outgoingMessagesHandler(ctx, port)
			},
			h.outgoingMessagesLoggerProducer,
		),
	)

	// Wait for both handlers to finish and return any error
	err = g.Wait()

	// Close the port
	if closeErr := port.Close(); closeErr != nil {
		h.handlerLoggerProducer.Warning(
			fmt.Sprintf(
				"An error occurred while closing the serial port: %v",
				closeErr,
			),
		)
	}
	return err
}

// incomingMessagesHandler processes incoming messages from the serial port.
//
// Parameters:
//
// ctx: The context to control the lifecycle of the handler.
// port: The serial port to read messages from.
//
// Returns:
//
// An error if any issue occurs during processing.
func (h *DefaultHandler) incomingMessagesHandler(
	ctx context.Context,
	port serial.Port,
) error {
	// Waiting for start message
	h.incomingMessagesLoggerProducer.Info("Waiting for start message...")
	for !h.receivedStartMessage {
		select {
		case <-ctx.Done():
			return ctx.Err()
		default:
			// Read incoming messages
			messages, err := h.readIncomingMessages(port)
			if err != nil {
				return err
			}

			// Send each message to the incoming messages channel
			for _, message := range messages {
				if h.receivedStartMessage {
					break
				}

				switch message.Category {
				case IncomingCategoryError:
					err := fmt.Errorf(
						"received error message: %s",
						message.Data,
					)
					h.incomingMessagesLoggerProducer.Error(err)
					return err
				case IncomingCategoryStatus:
					// Check if it's a start message
					if message.IsStatusStartMessage() {
						h.receivedStartMessage = true
						h.incomingMessagesLoggerProducer.Info("Received start message")

						// Send a confirmation message
						h.outgoingMessagesCh <- OutgoingOKMessage

						// Log the confirmation message sent
						h.outgoingMessagesLoggerProducer.Info("Sent start confirmation message")
						break
					}
					fallthrough

				default:
					// Log any other received message
					h.incomingMessagesLoggerProducer.Info(
						fmt.Sprintf(
							"Received message while waiting for start message: %s",
							message.StringToPrint(),
						),
					)
				}
			}
		}
	}

	// Wait for challenge message
	h.incomingMessagesLoggerProducer.Info("Waiting for challenge message...")
	for h.receivedChallenge == internal.ChallengeNil {
		select {
		case <-ctx.Done():
			return ctx.Err()
		default:
			// Read incoming messages
			messages, err := h.readIncomingMessages(port)
			if err != nil {
				return err
			}

			// Send each message to the incoming messages channel
			for _, message := range messages {
				if h.receivedChallenge != internal.ChallengeNil {
					break
				}

				switch message.Category {
				case IncomingCategoryError:
					err := fmt.Errorf(
						"received error message: %s",
						message.Data,
					)
					h.incomingMessagesLoggerProducer.Error(
						fmt.Errorf(
							"Received error message: %w",
							err,
						),
					)
					return err
				case IncomingCategoryStatus:
					// Check if it's a start message
					if message.IsStatusStartMessage() {
						// Resend a confirmation message
						h.outgoingMessagesCh <- OutgoingOKMessage

						// Log the confirmation message sent
						h.outgoingMessagesLoggerProducer.Info("Sent start confirmation message again")
					}
				case IncomingCategoryChallenge:
					challenge, err := internal.ChallengeFromBytes(message.Data)
					if err != nil {
						return fmt.Errorf(
							"failed to parse challenge message data: %w",
							err,
						)
					}
					h.receivedChallenge = challenge
					h.incomingMessagesLoggerProducer.Info(
						fmt.Sprintf(
							"Received challenge: %s",
							challenge.String(),
						),
					)

					// Notify listeners exactly once
					h.notifyChallengeOnce.Do(func() { close(h.challengeReadyCh) })

					// Send a confirmation message
					h.outgoingMessagesCh <- OutgoingOKMessage

					// Log the confirmation message sent
					h.outgoingMessagesLoggerProducer.Info("Sent challenge confirmation message")
				default:
					// Log any other received message
					h.incomingMessagesLoggerProducer.Info(
						fmt.Sprintf(
							"Received message while waiting for challenge message: %s",
							message.StringToPrint(),
						),
					)
				}
			}
		}
	}

	// Mark the handler as started
	h.hasStarted.Store(true)

	for {
		select {
		case <-ctx.Done():
			return ctx.Err()
		default:
			// Read incoming messages
			messages, err := h.readIncomingMessages(port)
			if err != nil {
				return err
			}

			// Send each message to the incoming messages channel
			for _, message := range messages {
				switch message.Category {
				case IncomingCategoryError:
					// Get the error code as a uint16
					errorCode := binary.BigEndian.Uint16(message.Data[:2])

					// Get the error code message
					errorCodeMessage, ok := GetErrorCodeMessage(tinygoerrors.ErrorCode(errorCode))
					if !ok {
						errorCodeMessage = "unknown error code"
					}

					// Log the error message
					err = fmt.Errorf(
						"received error message: %s",
						errorCodeMessage,
					)
					h.incomingMessagesLoggerProducer.Warning(err.Error())
				case IncomingCategoryChallenge:
					// Resend a confirmation message
					h.outgoingMessagesCh <- OutgoingOKMessage

					// Log the confirmation message sent
					h.outgoingMessagesLoggerProducer.Info("Sent challenge confirmation message again")
				case IncomingCategoryEulerDegreesPitch:
					// Parse the BNO08X pitch degrees value
					degreesUint64 := binary.BigEndian.Uint64(message.Data[:8])
					degrees := math.Float64frombits(degreesUint64)
					h.updateBNO08XPitchDegrees(degrees)
				case IncomingCategoryEulerDegreesRoll:
					// Parse the BNO08X roll degrees value
					degreesUint64 := binary.BigEndian.Uint64(message.Data[:8])
					degrees := math.Float64frombits(degreesUint64)
					h.updateBNO08XRollDegrees(degrees)
				case IncomingCategoryEulerDegreesYaw:
					// Parse the BNO08X yaw degrees value
					degreesUint64 := binary.BigEndian.Uint64(message.Data[:8])
					degrees := math.Float64frombits(degreesUint64)
					h.updateBNO08XYawDegrees(degrees)
				case IncomingCategoryQuaternionX:
					// Parse the BNO08X quaternion X value
					quaternionXUint64 := binary.BigEndian.Uint64(message.Data[:8])
					h.receivedBNO08XQuaternionX = math.Float64frombits(quaternionXUint64)
				case IncomingCategoryQuaternionY:
					// Parse the BNO08X quaternion Y value
					quaternionYUint64 := binary.BigEndian.Uint64(message.Data[:8])
					h.receivedBNO08XQuaternionY = math.Float64frombits(quaternionYUint64)
				case IncomingCategoryQuaternionZ:
					// Parse the BNO08X quaternion Z value
					quaternionZUint64 := binary.BigEndian.Uint64(message.Data[:8])
					h.receivedBNO08XQuaternionZ = math.Float64frombits(quaternionZUint64)
				case IncomingCategoryQuaternionW:
					// Parse the BNO08X quaternion W value
					quaternionWUint64 := binary.BigEndian.Uint64(message.Data[:8])
					h.receivedBNO08XQuaternionW = math.Float64frombits(quaternionWUint64)

					// Convert the quaternion to Euler angles in degrees
					var quaternion [4]float64
					quaternion[QuaternionWIndex] = h.receivedBNO08XQuaternionW
					quaternion[QuaternionXIndex] = h.receivedBNO08XQuaternionX
					quaternion[QuaternionYIndex] = h.receivedBNO08XQuaternionY
					quaternion[QuaternionZIndex] = h.receivedBNO08XQuaternionZ
					eulerDegrees := QuaternionToEulerDegrees(
						quaternion,
					)

					// Update the received Euler angles
					h.updateBNO08XYawDegrees(eulerDegrees[EulerDegreesYawIndex])
					h.updateBNO08XPitchDegrees(eulerDegrees[EulerDegreesPitchIndex])
					h.updateBNO08XRollDegrees(eulerDegrees[EulerDegreesRollIndex])
				case IncomingCategoryMotorSpeedStart:
					h.incomingMessagesLoggerProducer.Info(
						"Received motor speed start message",
					)
					h.motorSpeedStartMessagesCh <- struct{}{}
				case IncomingCategoryMotorSpeedEnd:
					h.incomingMessagesLoggerProducer.Info(
						"Received motor speed end message",
					)
					h.motorSpeedEndMessagesCh <- struct{}{}
				case IncomingCategoryServoAngleStart:
					h.incomingMessagesLoggerProducer.Info(
						"Received servo angle start message",
					)
					h.servoAngleStartMessagesCh <- struct{}{}
				case IncomingCategoryServoAngleEnd:
					h.incomingMessagesLoggerProducer.Info(
						"Received servo angle end message",
					)
					h.servoAngleEndMessagesCh <- struct{}{}
				default:
					// Log any other received message
					h.incomingMessagesLoggerProducer.Info(
						fmt.Sprintf(
							"Received message: %s",
							message.StringToPrint(),
						),
					)
				}
			}
		}
	}
}

// updateYawDegreesHandler updates based on the received yaw degrees.
func (h *DefaultHandler) updateYawDegreesHandler() {
	if h.yawDegreesHandler == nil {
		h.yawDegreesHandler = NewYawDegreesHandler(h.receivedBNO08XYawDegrees)
		h.incomingMessagesLoggerProducer.Info(
			fmt.Sprintf(
				"Initial yaw degrees: %f",
				h.receivedBNO08XYawDegrees,
			),
		)
		return
	}

	// Update the yaw degrees handler
	h.yawDegreesHandler.Update(h.receivedBNO08XYawDegrees)

	if h.incomingMessagesLoggerProducer.IsDebug() {
		h.incomingMessagesLoggerProducer.Debug(
			fmt.Sprintf(
				"Updated accumulated yaw degrees: %.3f",
				h.yawDegreesHandler.GetAccumulatedYawDegrees(),
			),
		)
	}
}

// updateBNO08XYawDegrees updates the BNO08X yaw degrees and recalculates the turns.
//
// Parameters:
//
// yawDegrees: The new yaw degrees to set.
func (h *DefaultHandler) updateBNO08XYawDegrees(yawDegrees float64) {
	// Validate the yaw degrees
	if yawDegrees < EulerDegreesYawMinValue || yawDegrees > EulerDegreesYawMaxValue {
		h.incomingMessagesLoggerProducer.Warning(
			fmt.Sprintf(
				"Invalid yaw degrees value: %f. Must be between %f and %f.",
				yawDegrees,
				EulerDegreesYawMinValue,
				EulerDegreesYawMaxValue,
			),
		)
		return
	}

	// Update the received yaw degrees
	h.receivedBNO08XYawDegrees = yawDegrees
	if h.incomingMessagesLoggerProducer.IsDebug() {
		h.incomingMessagesLoggerProducer.Debug(
			fmt.Sprintf(
				"Updated BNO08X yaw degrees: %f",
				h.receivedBNO08XYawDegrees,
			),
		)
	}

	// Update the yaw degrees handler
	h.updateYawDegreesHandler()
}

// updateBNO08XPitchDegrees updates the BNO08X pitch degrees.
//
// Parameters:
//
// pitchDegrees: The new pitch degrees to set.
func (h *DefaultHandler) updateBNO08XPitchDegrees(pitchDegrees float64) {
	// Validate the pitch degrees
	if pitchDegrees < EulerDegreesPitchMinValue || pitchDegrees > EulerDegreesPitchMaxValue {
		h.incomingMessagesLoggerProducer.Warning(
			fmt.Sprintf(
				"Invalid pitch degrees value: %f. Must be between %f and %f.",
				pitchDegrees,
				EulerDegreesPitchMinValue,
				EulerDegreesPitchMaxValue,
			),
		)
		return
	}

	// Update the received pitch degrees
	h.receivedBNO08XPitchDegrees = pitchDegrees
	if h.incomingMessagesLoggerProducer.IsDebug() {
		h.incomingMessagesLoggerProducer.Debug(
			fmt.Sprintf(
				"Updated BNO08X pitch degrees: %f",
				h.receivedBNO08XPitchDegrees,
			),
		)
	}
}

// updateBNO08XRollDegrees updates the BNO08X roll degrees.
//
// Parameters:
//
// rollDegrees: The new roll degrees to set.
func (h *DefaultHandler) updateBNO08XRollDegrees(rollDegrees float64) {
	// Validate the roll degrees
	if rollDegrees < EulerDegreesRollMinValue || rollDegrees > EulerDegreesRollMaxValue {
		h.incomingMessagesLoggerProducer.Warning(
			fmt.Sprintf(
				"Invalid roll degrees value: %f. Must be between %f and %f.",
				rollDegrees,
				EulerDegreesRollMinValue,
				EulerDegreesRollMaxValue,
			),
		)
		return
	}

	// Update the received roll degrees
	h.receivedBNO08XRollDegrees = rollDegrees
	if h.incomingMessagesLoggerProducer.IsDebug() {
		h.incomingMessagesLoggerProducer.Debug(
			fmt.Sprintf(
				"Updated BNO08X roll degrees: %f",
				h.receivedBNO08XRollDegrees,
			),
		)
	}
}

// readFromPort reads data from the serial port.
//
// Parameters:
//
// port: The serial port to read data from.
//
// Returns:
//
// An error if any issue occurs during reading.
func (h *DefaultHandler) readFromPort(port serial.Port) error {
	n, err := port.Read(h.buffer)
	if err != nil {
		return fmt.Errorf(
			"an error occurred while reading from the serial port: %v",
			err,
		)
	}
	if n == 0 {
		// Read can return 0 bytes
		return nil
	}

	// Process the data read
	h.accumulatedBuffer = append(
		h.accumulatedBuffer,
		h.buffer[:n]...,
	)
	return nil
}

// readIncomingMessages reads incoming messages from the serial port.
//
// Parameters:
//
// port: The serial port to read messages from.
//
// Returns:
//
// A slice of IncomingMessage pointers or an error if any issue occurs during reading or parsing.
func (h *DefaultHandler) readIncomingMessages(
	port serial.Port,
) ([]*IncomingMessage, error) {
	// Read data from the port
	if err := h.readFromPort(port); err != nil {
		return nil, fmt.Errorf("failed to read from port: %w", err)
	}

	if len(h.accumulatedBuffer) == 0 {
		return nil, nil
	}

	// Log the accumulated buffer data
	if h.incomingMessagesLoggerProducer.IsDebug() {
		h.incomingMessagesLoggerProducer.Debug(
			fmt.Sprintf(
				"Accumulated buffer data: %s",
				ConvertBytesSliceToHexString(h.accumulatedBuffer),
			),
		)
	}

	// Extract messages from the accumulated buffer
	messages, err := NewIncomingMessagesFromBuffer(
		&h.accumulatedBuffer,
		h.incomingMessagesLoggerProducer,
	)
	if err != nil {
		return nil, fmt.Errorf(
			"failed to extract incoming messages from buffer: %w",
			err,
		)
	}

	return messages, nil
}

// outgoingMessagesHandler processes outgoing messages and sends them through the serial port.
//
// Parameters:
//
// ctx: The context to control the lifecycle of the handler.
// port: The serial port to send messages through.
//
// Returns:
//
// An error if any issue occurs during processing.
func (h *DefaultHandler) outgoingMessagesHandler(
	ctx context.Context,
	port serial.Port,
) error {
	// Track the last heartbeat time
	lastHeartbeatTime := time.Now()
	for {
		select {
		case <-ctx.Done():
			// Send the final stop message
			if err := h.sendMessage(port, OutgoingStopMessage); err != nil {
				return err
			}

			// Log the stop message sent
			h.outgoingMessagesLoggerProducer.Info("Sent stop message, waiting for confirmation...")

			// Wait for a stop confirmation message or timeout
			initialTime := time.Now()
			for time.Since(initialTime) < StopTimeout {
				// Read any remaining incoming messages and check if they are stop confirmations
				incomingMessages, err := h.readIncomingMessages(port)
				if err != nil {
					return err
				}

				for _, message := range incomingMessages {
					if message.IsEqual(IncomingOKMessage) {
						h.outgoingMessagesLoggerProducer.Info("Received stop confirmation message")
						return nil
					}
				}
			}
			h.outgoingMessagesLoggerProducer.Warning("Did not receive stop confirmation message before timeout")
			return ctx.Err()
		case outgoingMessage, ok := <-h.outgoingMessagesCh:
			if !ok {
				return ErrOutgoingMessagesChannelClosedAheadOfTime
			}
			if err := h.sendMessage(port, outgoingMessage); err != nil {
				return err
			}
		default:
			// Check if it's time to send a heartbeat message and the handler has started
			if h.hasStarted.Load() && time.Since(lastHeartbeatTime) >= HeartbeatInterval {
				// Send a heartbeat message if the interval has passed
				if err := h.sendMessage(
					port,
					OutgoingHeartbeatMessage,
				); err != nil {
					return err
				}
				lastHeartbeatTime = time.Now()

				// Log the heartbeat message sent
				if h.outgoingMessagesLoggerProducer.IsDebug() {
					h.outgoingMessagesLoggerProducer.Debug("Sent heartbeat message")
				}
			}
		}
	}
}

// sendMessage sends a message through the serial port.
//
// Parameters:
//
// port: The serial port to send the message through.
// message: Pointer to the OutgoingMessage to be sent.
//
// Returns:
//
// An error if the message could not be sent.
func (h *DefaultHandler) sendMessage(
	port serial.Port,
	message *OutgoingMessage,
) error {
	// Check if the message is nil
	if message == nil {
		h.outgoingMessagesLoggerProducer.Warning("Attempted to send a nil outgoing message")
		return nil
	}
	messageBytes := []byte{StartAndEndByte, byte(message.Category)}

	// Get the data length
	dataLength := len(message.Data)

	// Verify data length corresponds for the given message category
	expectedDataLength, err := message.Category.DataLength()
	if err != nil {
		return fmt.Errorf("failed to get expected data length: %w", err)
	}
	if dataLength != expectedDataLength {
		return fmt.Errorf(
			ErrDataLengthMismatchForOutgoingMessage,
			message.Category,
			dataLength,
			expectedDataLength,
		)
	}

	// Add data length byte
	messageBytes = append(messageBytes, uint8(dataLength))

	// Escape and add data bytes
	for _, b := range message.Data {
		if b == StartAndEndByte || b == ControlByte {
			messageBytes = append(messageBytes, ControlByte)
			b ^= XORByte
		}
		messageBytes = append(messageBytes, b)
	}

	// Calculate and add checksum byte
	checksum := CalculateChecksum(byte(message.Category), message.Data)
	messageBytes = append(messageBytes, checksum)

	// Add end byte
	messageBytes = append(messageBytes, StartAndEndByte)

	// Log the message to be sent
	if h.outgoingMessagesLoggerProducer.IsDebug() {
		h.outgoingMessagesLoggerProducer.Debug(
			fmt.Sprintf(
				"Sending message bytes: %s",
				ConvertBytesSliceToHexString(messageBytes),
			),
		)
	}

	// Write the message bytes to the port
	if _, err = port.Write(messageBytes); err != nil {
		return fmt.Errorf("failed to write message to port: %w", err)
	}

	// Log the message sent
	if h.outgoingMessagesLoggerProducer.IsDebug() {
		h.outgoingMessagesLoggerProducer.Info(
			fmt.Sprintf(
				"Sent message: %s",
				message.StringToPrint(),
			),
		)
	}
	return nil
}

// Run starts the handler to read from and write to the serial port.
//
// Parameters:
//
// ctx: Context for managing cancellation and timeouts.
// cancelFn: Function to call to cancel the context.
//
// Returns:
//
// An error if any issue occurs during reading or writing.
func (h *DefaultHandler) Run(ctx context.Context, cancelFn context.CancelFunc) error {
	h.mutex.Lock()

	// Check if it's already running
	if h.IsRunning() {
		h.mutex.Unlock()
		return ErrHandlerAlreadyRunning
	}
	defer h.close()

	// Set running to true
	h.isRunning.Store(true)

	// Reset the hasStarted state
	h.hasStarted.Store(false)

	// Initialize the outgoing messages channel
	h.outgoingMessagesCh = make(
		chan *OutgoingMessage,
		OutgoingMessagesChannelBufferSize,
	)
	close(h.readyCh)

	// Initialize motor speed messages channel
	h.motorSpeedStartMessagesCh = make(
		chan struct{},
	)
	h.motorSpeedEndMessagesCh = make(
		chan struct{},
	)

	// Initialize servo angle messages channel
	h.servoAngleStartMessagesCh = make(
		chan struct{},
	)
	h.servoAngleEndMessagesCh = make(
		chan struct{},
	)

	// Reset received start message state
	h.receivedStartMessage = false

	// Reset received challenge
	h.receivedChallenge = internal.ChallengeNil
	h.challengeReadyCh = make(chan struct{})
	h.notifyChallengeOnce = sync.Once{}

	// Reset BNO08X yaw degrees handler
	h.yawDegreesHandler = nil

	// Reset received BNO08X quaternion values
	h.receivedBNO08XQuaternionX = 0.0
	h.receivedBNO08XQuaternionY = 0.0
	h.receivedBNO08XQuaternionZ = 0.0
	h.receivedBNO08XQuaternionW = 0.0

	// Reset received BNO08X yaw, pitch and roll degrees
	h.receivedBNO08XYawDegrees = 0.0
	h.receivedBNO08XPitchDegrees = 0.0
	h.receivedBNO08XRollDegrees = 0.0

	// Clear the accumulated buffer
	h.accumulatedBuffer = h.accumulatedBuffer[:0]

	h.mutex.Unlock()

	// Create a logger producer
	handlerLoggerProducer, err := h.logger.NewProducer(
		HandlerLoggerProducerTag,
		h.debug,
	)
	if err != nil {
		return fmt.Errorf("failed to create logger producer: %w", err)
	}
	h.handlerLoggerProducer = handlerLoggerProducer
	defer h.handlerLoggerProducer.Close()

	return goconcurrentlogger.CancelContextAndLogOnError(
		ctx,
		cancelFn,
		func(ctx context.Context) error {
			return h.runToWrap(ctx, cancelFn)
		},
		h.handlerLoggerProducer,
	)()
}

// NewSender returns a new Sender instance associated with this DefaultHandler.
//
// Parameters:
//
// tag: Tag to identify the sender instance.
//
// Returns:
//
// A pointer to a Sender instance or an error if the parameters are invalid.
func (h *DefaultHandler) NewSender() (Sender, error) {
	h.mutex.Lock()
	defer h.mutex.Unlock()

	// Check if the handler is already closed
	if !h.IsRunning() {
		return nil, ErrHandlerClosed
	}

	// Check if the outgoing messages channel is initialized
	if h.outgoingMessagesCh == nil {
		return nil, ErrHandlerNotRunning
	}

	// Increment the producer wait group counter
	h.wgSenders.Add(1)

	// Create and return a new DefaultSender instance
	handlerLoggerProducer, err := NewDefaultSender(
		func(m *OutgoingMessage) {
			h.outgoingMessagesCh <- m
		},
		func() { h.wgSenders.Done() },
	)
	if err != nil {
		h.wgSenders.Done()
		return nil, err
	}
	return handlerLoggerProducer, nil
}

// close signals no more senders will send; safe to call multiple times.
func (h *DefaultHandler) close() {
	h.mutex.Lock()

	// Check if the handler is already closed
	if !h.IsRunning() { 
		h.mutex.Unlock()
		return
	}

	// Mark the handler as closed
	h.isRunning.Store(false)

	h.mutex.Unlock()

	// Wait for all registered producers to finish, then close channel.
	h.wgSenders.Wait()

	// Close the outgoing messages channel to signal no more messages will be sent.
	close(h.outgoingMessagesCh)
	h.outgoingMessagesCh = nil

	// Close the motor speed messages channel
	close(h.motorSpeedStartMessagesCh)
	h.motorSpeedStartMessagesCh = nil
	close(h.motorSpeedEndMessagesCh)
	h.motorSpeedEndMessagesCh = nil

	// Close the servo angle messages channel
	close(h.servoAngleStartMessagesCh)
	h.servoAngleStartMessagesCh = nil
	close(h.servoAngleEndMessagesCh)
	h.servoAngleEndMessagesCh = nil

	// Initialize the ready channel for the next run
	h.readyCh = make(chan struct{})

	// Reset the producer wait group
	h.wgSenders = sync.WaitGroup{}
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
func (h *DefaultHandler) WaitUntilReady(ctx context.Context) error {
	select {
	case <-ctx.Done():
		return ctx.Err()
	case <-h.readyCh:
		return nil
	}
}

// ClearMotorSpeedStartMessagesCh clears any pending motor speed start messages.
func (h *DefaultHandler) ClearMotorSpeedStartMessagesCh() {
	// Check if the handler is running
	if h.motorSpeedStartMessagesCh == nil {
		return
	}

	// Clear any pending messages
	for {
		select {
		case <-h.motorSpeedStartMessagesCh:
		default:
			return
		}
	}
}

// WaitMotorSpeedStartMessage waits for a motor speed start message or the context is done.
//
// Parameters:
//
// ctx: The context to control cancellation and timeouts.
//
// Returns:
//
// An error if the context is done before receiving the motor speed start message.
func (h *DefaultHandler) WaitMotorSpeedStartMessage(ctx context.Context) error {
	// Check if the handler is running
	if h.motorSpeedStartMessagesCh == nil {
		return ErrHandlerNotRunning
	}

	select {
	case <-ctx.Done():
		return ctx.Err()
	case _, ok := <-h.motorSpeedStartMessagesCh:
		// Check if the handler has been closed
		if !ok {
			return ErrHandlerClosed
		}
		return nil
	}
}

// ClearMotorSpeedEndMessagesCh clears any pending motor speed end messages.
func (h *DefaultHandler) ClearMotorSpeedEndMessagesCh() {
	// Check if the handler is running
	if h.motorSpeedEndMessagesCh == nil {
		return
	}

	// Clear any pending messages
	for {
		select {
		case <-h.motorSpeedEndMessagesCh:
		default:
			return
		}
	}
}

// WaitMotorSpeedEndMessage waits for a motor speed end message or the context is done.
//
// Parameters:
//
// ctx: The context to control cancellation and timeouts.
//
// Returns:
//
// An error if the context is done before receiving the motor speed end message.
func (h *DefaultHandler) WaitMotorSpeedEndMessage(ctx context.Context) error {
	// Check if the handler is running
	if h.motorSpeedEndMessagesCh == nil {
		return ErrHandlerNotRunning
	}

	select {
	case <-ctx.Done():
		return ctx.Err()
	case _, ok := <-h.motorSpeedEndMessagesCh:
		// Check if the handler has been closed
		if !ok {
			return ErrHandlerClosed
		}
		return nil
	}
}

// ClearMotorSpeedStartAndEndMessagesCh clears any pending motor speed start and end messages.
func (h *DefaultHandler) ClearMotorSpeedStartAndEndMessagesCh() {
	h.ClearMotorSpeedStartMessagesCh()
	h.ClearMotorSpeedEndMessagesCh()
}

// ClearServoAngleStartMessagesCh clears any pending servo angle start messages.
func (h *DefaultHandler) ClearServoAngleStartMessagesCh() {
	// Check if the handler is running
	if h.servoAngleStartMessagesCh == nil {
		return
	}

	// Clear any pending messages
	for {
		select {
		case <-h.servoAngleStartMessagesCh:
		default:
			return
		}
	}
}

// WaitServoAngleStartMessage waits for a servo angle start message or the context is done.
//
// Parameters:
//
// ctx: The context to control cancellation and timeouts.
//
// Returns:
//
// An error if the context is done before receiving the servo angle start message.
func (h *DefaultHandler) WaitServoAngleStartMessage(ctx context.Context) error {
	// Check if the handler is running
	if h.servoAngleStartMessagesCh == nil {
		return ErrHandlerNotRunning
	}

	select {
	case <-ctx.Done():
		return ctx.Err()
	case _, ok := <-h.servoAngleStartMessagesCh:
		// Check if the handler has been closed
		if !ok {
			return ErrHandlerClosed
		}
		return nil
	}
}

// ClearServoAngleEndMessagesCh clears any pending servo angle end messages.
func (h *DefaultHandler) ClearServoAngleEndMessagesCh() {
	// Check if the handler is running
	if h.servoAngleEndMessagesCh == nil {
		return
	}

	// Clear any pending messages
	for {
		select {
		case <-h.servoAngleEndMessagesCh:
		default:
			return
		}
	}
}

// WaitServoAngleEndMessage waits for a servo angle end message or the context is done.
//
// Parameters:
//
// ctx: The context to control cancellation and timeouts.
//
// Returns:
//
// An error if the context is done before receiving the servo angle end message.
func (h *DefaultHandler) WaitServoAngleEndMessage(ctx context.Context) error {
	// Check if the handler is running
	if h.servoAngleEndMessagesCh == nil {
		return ErrHandlerNotRunning
	}

	select {
	case <-ctx.Done():
		return ctx.Err()
	case _, ok := <-h.servoAngleEndMessagesCh:
		// Check if the handler has been closed
		if !ok {
			return ErrHandlerClosed
		}
		return nil
	}
}

// ClearServoAngleStartAndEndMessagesCh clears any pending servo angle start and end messages.
func (h *DefaultHandler) ClearServoAngleStartAndEndMessagesCh() {
	h.ClearServoAngleStartMessagesCh()
	h.ClearServoAngleEndMessagesCh()
}

// ReceivedStartMessage returns true if the start message has been received.
//
// Returns:
//
// True if the start message has been received, otherwise false.
func (h *DefaultHandler) ReceivedStartMessage() bool {
	h.mutex.Lock()
	defer h.mutex.Unlock()
	return h.receivedStartMessage
}

// ReceivedChallenge returns the received challenge.
//
// Returns:
//
// The received challenge.
func (h *DefaultHandler) ReceivedChallenge() internal.Challenge {
	h.mutex.Lock()
	defer h.mutex.Unlock()
	return h.receivedChallenge
}

// Get360DegreeTurns returns the total number of 360-degree turns made.
//
// Returns:
//
// The total number of 360-degree turns made.
func (h *DefaultHandler) Get360DegreeTurns() uint {
	h.mutex.Lock()
	defer h.mutex.Unlock()
	if h.yawDegreesHandler == nil {
		return 0
	}
	return uint(h.yawDegreesHandler.getNDegreeTurns(360))
}

// Get90DegreeTurns returns the total number of 90-degree turns made.
//
// Returns:
//
// The total number of 90-degree turns made.
func (h *DefaultHandler) Get90DegreeTurns() uint {
	h.mutex.Lock()
	defer h.mutex.Unlock()
	if h.yawDegreesHandler == nil {
		return 0
	}
	return uint(h.yawDegreesHandler.getNDegreeTurns(90))
}

// Get45DegreeTurns returns the total number of 45-degree turns made.
//
// Returns:
//
// The total number of 45-degree turns made.
func (h *DefaultHandler) Get45DegreeTurns() uint {
	h.mutex.Lock()
	defer h.mutex.Unlock()
	if h.yawDegreesHandler == nil {
		return 0
	}
	return uint(h.yawDegreesHandler.getNDegreeTurns(45))
}

// Get30DegreeTurns returns the total number of 30-degree turns made.
//
// Returns:
//
// The total number of 30-degree turns made.
func (h *DefaultHandler) Get30DegreeTurns() uint {
	h.mutex.Lock()
	defer h.mutex.Unlock()
	if h.yawDegreesHandler == nil {
		return 0
	}
	return uint(h.yawDegreesHandler.getNDegreeTurns(30))
}

// GetAccumulatedYawDegrees returns the accumulated yaw degrees.
//
// Returns:
//
// The accumulated yaw degrees.	
func (h *DefaultHandler) GetAccumulatedYawDegrees() float64 {
	h.mutex.Lock()
	defer h.mutex.Unlock()
	if h.yawDegreesHandler == nil {
		return 0.0
	}
	return h.yawDegreesHandler.GetAccumulatedYawDegrees()
}

// ReceivedBNO08XYawDegrees returns the received BNO08X yaw degrees.
//
// Returns:
//
// The received BNO08X yaw degrees.
func (h *DefaultHandler) ReceivedBNO08XYawDegrees() float64 {
	h.mutex.Lock()
	defer h.mutex.Unlock()
	return h.receivedBNO08XYawDegrees
}

// ReceivedBNO08XPitchDegrees returns the received BNO08X pitch degrees.
//
// Returns:
//
// The received BNO08X pitch degrees.
func (h *DefaultHandler) ReceivedBNO08XPitchDegrees() float64 {
	h.mutex.Lock()
	defer h.mutex.Unlock()
	return h.receivedBNO08XPitchDegrees
}

// ReceivedBNO08XRollDegrees returns the received BNO08X roll degrees.
//
// Returns:
//
// The received BNO08X roll degrees.
func (h *DefaultHandler) ReceivedBNO08XRollDegrees() float64 {
	h.mutex.Lock()
	defer h.mutex.Unlock()
	return h.receivedBNO08XRollDegrees
}

// ReceivedBNO08XQuaternionX returns the received BNO08X quaternion X value.
//
// Returns:
//
// The received BNO08X quaternion X value.
func (h *DefaultHandler) ReceivedBNO08XQuaternionX() float64 {
	h.mutex.Lock()
	defer h.mutex.Unlock()
	return h.receivedBNO08XQuaternionX
}

// ReceivedBNO08XQuaternionY returns the received BNO08X quaternion Y value.
//
// Returns:
//
// The received BNO08X quaternion Y value.
func (h *DefaultHandler) ReceivedBNO08XQuaternionY() float64 {
	h.mutex.Lock()
	defer h.mutex.Unlock()
	return h.receivedBNO08XQuaternionY
}

// ReceivedBNO08XQuaternionZ returns the received BNO08X quaternion Z value.
//
// Returns:
//
// The received BNO08X quaternion Z value.
func (h *DefaultHandler) ReceivedBNO08XQuaternionZ() float64 {
	h.mutex.Lock()
	defer h.mutex.Unlock()
	return h.receivedBNO08XQuaternionZ
}

// ReceivedBNO08XQuaternionW returns the received BNO08X quaternion W value.
//
// Returns:
//
// The received BNO08X quaternion W value.
func (h *DefaultHandler) ReceivedBNO08XQuaternionW() float64 {
	h.mutex.Lock()
	defer h.mutex.Unlock()
	return h.receivedBNO08XQuaternionW
}

// WaitForChallenge waits until a challenge message is received or the context is done.
//
// Parameters:
//
// ctx: The context to control cancellation and timeouts.
//
// Returns:
//
// The received challenge or an error if the context is done before receiving it.
func (h *DefaultHandler) WaitForChallenge(ctx context.Context) (
	internal.Challenge,
	error,
) {
	if c := h.ReceivedChallenge(); c != internal.ChallengeNil {
		return c, nil
	}
	select {
	case <-ctx.Done():
		return internal.ChallengeNil, ctx.Err()
	case <-h.challengeReadyCh:
		return h.ReceivedChallenge(), nil
	}
}
