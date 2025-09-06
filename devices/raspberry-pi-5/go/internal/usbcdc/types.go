package usbcdc

import (
	"context"
	"fmt"
	"sync"
	"sync/atomic"
	"time"

	ralvarezdevgostringsconvert "github.com/ralvarezdev/go-strings/convert"
	"github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal"
	internallog "github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal/log"
	internalrplidar "github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal/rplidar"
	internalusbcdcenums "github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal/usbcdc/enums"
	"go.bug.st/serial"
	"golang.org/x/sync/errgroup"
)

type (
	// DefaultSender is the default implementation of the Sender interface
	DefaultSender struct {
		sendFn  func(*OutgoingMessage)
		closeFn func()
		mutex   sync.Mutex
		closed  atomic.Bool
	}

	// DefaultHandler is the default implementation of the Handler interface
	DefaultHandler struct {
		outgoingMessagesCh               chan *OutgoingMessage
		logger                           internallog.Logger
		handlerLoggerProducer                   internallog.LoggerProducer
		incomingMessagesLoggerProducer           internallog.LoggerProducer
		outgoingMessagesLoggerProducer          internallog.LoggerProducer
		isRunning                        atomic.Bool
		closed                           atomic.Bool
		mutex                            sync.Mutex
		wgSenders                        sync.WaitGroup
		baudRate                         int
		buffer                           []byte
		accumulatedBuffer                []byte
		receivedInitializationMessage    bool
		receivedStartMessage             bool
		receivedChallenge                internal.Challenge
		receivedMaxMotorSpeedValue       uint16
		receivedMaxServoDirectionValue   uint16
		receivedBNO08XTurns              int
		receivedBNO08XYawDegrees         float64
		challengeReady                   chan struct{}
		notifyChallengeOnce              sync.Once
		maxMotorSpeedValueReady          chan struct{}
		notifyMaxMotorSpeedValueOnce     sync.Once
		maxServoDirectionValueReady      chan struct{}
		notifyMaxServoDirectionValueOnce sync.Once
	}
)

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
	s.mutex.Lock()
	defer s.mutex.Unlock()
	return s.closed.Load()
}

// NewDefaultHandler creates a new DefaultHandler instance
//
// Parameters:
//
// baudRate: Baud rate for the serial communication.
// logger: Logger instance for logging messages.
//
// Returns:
//
// A pointer to a DefaultHandler instance
func NewDefaultHandler(baudRate int, logger internallog.Logger) (*DefaultHandler, error) {
	// Check if the logger is nil
	if logger == nil {
		return nil, internallog.ErrNilLogger
	}
	
	// Create a buffer for reading data
	buffer := make([]byte, BufferSize)

	// Create an accumulated buffer for storing data
	accumulatedBuffer := make([]byte, 0)

	return &DefaultHandler{
		baudRate:          baudRate,
		buffer:            buffer,
		accumulatedBuffer: accumulatedBuffer,
		logger:           logger,
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
// stopFn: Function to call when stopping the handler.
//
// Returns:
//
// An error if any issue occurs during reading or writing.
func (h *DefaultHandler) runToWrap(ctx context.Context, stopFn func()) error {
	// Create a logger producers
	incomingMessagesLoggerProducer, err := h.logger.NewProducer(
		IncomingMessagesLoggerProducerTag,
	)
	if err != nil {
		return fmt.Errorf("failed to create incoming messages logger producer: %w", err)
	}
	h.incomingMessagesLoggerProducer = incomingMessagesLoggerProducer
	defer h.incomingMessagesLoggerProducer.Close()

	outgoingMessagesLoggerProducer, err := h.logger.NewProducer(
		OutgoingMessagesLoggerProducerTag,
	)
	if err != nil {
		return fmt.Errorf("failed to create outgoing messages logger producer: %w", err)
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
		if p != internalrplidar.SlamtecC1Port {
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
		internallog.StopContextAndLogOnError(
			ctx,
			stopFn, 
			func(ctx context.Context) error {
					return h.incomingMessagesHandler(ctx, port)
				},
			h.incomingMessagesLoggerProducer,
		),	
	)

	// Call the outgoing messages handler
	g.Go(
		internallog.StopContextAndLogOnError(
			ctx,
			stopFn, 
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
	// Received initialization message
	h.incomingMessagesLoggerProducer.Info("Waiting for initialization message...")
	for !h.receivedInitializationMessage {
		select {
		case <-ctx.Done():
			return ctx.Err()
		default:
			// Read data from the port
			if err := h.readFromPort(port); err != nil {
				return err
			}

			// Process the data read
			for _, c := range h.accumulatedBuffer {
				if c == InitializationMessage {
					h.receivedInitializationMessage = true
					h.incomingMessagesLoggerProducer.Info("Received initialization message")
					break
				}
			}
		}
	}

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
				case internalusbcdcenums.IncomingCategoryError:
					err := fmt.Errorf("received error message: %s", message.Content)
					h.incomingMessagesLoggerProducer.Error(err)
					return err
				case internalusbcdcenums.IncomingCategoryChallenge:
					h.receivedStartMessage = true
					h.incomingMessagesLoggerProducer.Info("Received start message")

					// Send a confirmation message
					h.outgoingMessagesCh <- OutgoingOKMessage
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
				if h.receivedChallenge == internal.ChallengeNil {
					break
				}

				switch message.Category {
				case internalusbcdcenums.IncomingCategoryError:
					err := fmt.Errorf("received error message: %s", message.Content)
					h.incomingMessagesLoggerProducer.Error(err)
					return err
				case internalusbcdcenums.IncomingCategoryChallenge:
					challenge, err := internal.ChallengeFromString(message.Content)
					if err != nil {
						return fmt.Errorf("failed to parse challenge message content: %w", err)
					}
					h.receivedChallenge = challenge
					h.incomingMessagesLoggerProducer.Info(
						fmt.Sprintf(
							"Received challenge: %s",
							challenge.Name(),
						),
					)

					// Notify listeners exactly once
					h.notifyChallengeOnce.Do(func() { close(h.challengeReady) })

					// Send a confirmation message
					h.outgoingMessagesCh <- OutgoingOKMessage
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

	// Send the message to get the max motor speed value and max servo direction value
	h.outgoingMessagesCh <- OutgoingGetMaxMotorSpeedValueMessage
	h.outgoingMessagesCh <- OutgoingGetMaxServoDirectionValueMessage

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
				case internalusbcdcenums.IncomingCategoryChallenge:
					err := fmt.Errorf("received error message: %s", message.Content)
					h.incomingMessagesLoggerProducer.Error(err)
					return err
				case internalusbcdcenums.IncomingCategoryDebug:
					debug, err := internalusbcdcenums.DebugFromString(message.Content)
					if err != nil {
						return fmt.Errorf("failed to parse debug message content: %w", err)
					}
					h.incomingMessagesLoggerProducer.Info(
						fmt.Sprintf(
							"Received debug: %s",
							debug.Name(),
						),
					)
				case internalusbcdcenums.IncomingCategoryBNO08XYawDegrees:
					// Parse the BNO08X yaw degrees value
					if err := ralvarezdevgostringsconvert.ToFloat64(
						message.Content,
						&h.receivedBNO08XYawDegrees,
					); err != nil {
						return fmt.Errorf(
							"failed to parse BNO08X yaw degrees message content: %w",
							err,
						)
					}

					// Log the received message
					h.incomingMessagesLoggerProducer.Info(
						fmt.Sprintf(
							"Received BNO08X yaw degrees: %f",
							h.receivedBNO08XYawDegrees,
						),
					)
				case internalusbcdcenums.IncomingCategoryBNO08XYawTurns:
					// Parse the BNO08X turns value
					if err := ralvarezdevgostringsconvert.ToInt(
						message.Content,
						&h.receivedBNO08XTurns,
					); err != nil {
						return fmt.Errorf(
							"failed to parse BNO08X turns message content: %w",
							err,
						)
					}

					// Log the received message
					h.incomingMessagesLoggerProducer.Info(
						fmt.Sprintf(
							"Received BNO08X turns: %d",
							h.receivedBNO08XTurns,
						),
					)
				case internalusbcdcenums.IncomingCategoryMaxMotorSpeedValue:
					// Parse the max motor speed value
					if err := ralvarezdevgostringsconvert.ToUint16(
						message.Content,
						&h.receivedMaxMotorSpeedValue,
					); err != nil {
						return fmt.Errorf(
							"failed to parse max motor speed value message content: %w",
							err,
						)
					}

					// Log the received message
					h.incomingMessagesLoggerProducer.Info(
						fmt.Sprintf(
							"Received max motor speed value: %d",
							h.receivedMaxMotorSpeedValue,
						),
					)

					// Notify listeners exactly once
					h.notifyMaxMotorSpeedValueOnce.Do(func() { close(h.maxMotorSpeedValueReady) })
				case internalusbcdcenums.IncomingCategoryMaxServoDirectionValue:
					// Parse the max servo direction value
					if err := ralvarezdevgostringsconvert.ToUint16(
						message.Content,
						&h.receivedMaxServoDirectionValue,
					); err != nil {
						return fmt.Errorf(
							"failed to parse max servo direction value message content: %w",
							err,
						)
					}

					// Log the received message
					h.incomingMessagesLoggerProducer.Info(
						fmt.Sprintf(
							"Received max servo direction value: %d",
							h.receivedMaxServoDirectionValue,
						),
					)

					// Notify listeners exactly once
					h.notifyMaxServoDirectionValueOnce.Do(func() { close(h.maxServoDirectionValueReady) })
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

	// Extract messages from the accumulated buffer
	messages, err := NewIncomingMessagesFromBuffer(&h.accumulatedBuffer)
	if err != nil {
		return nil, fmt.Errorf("failed to parse incoming messages: %w", err)
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

			return ctx.Err()
		case outgoingMessage, ok := <-h.outgoingMessagesCh:
			if !ok {
				return ErrOutgoingMessagesChannelClosedAheadOfTime
			}
			if err := h.sendMessage(port, outgoingMessage); err != nil {
				return err
			}
		default:
			if time.Since(lastHeartbeatTime) >= HeartbeatInterval {
				// Send a heartbeat message if the interval has passed
				h.outgoingMessagesLoggerProducer.Info("Sending heartbeat message")
				if err := h.sendMessage(
					port,
					OutgoingHeartbeatMessage,
				); err != nil {
					return err
				}
				lastHeartbeatTime = time.Now()
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

	// Send the message to the port
	if _, err := port.Write([]byte(message.String())); err != nil {
		return fmt.Errorf(ErrFailedToSendMessage, err)
	}

	// Log the message sent
	h.outgoingMessagesLoggerProducer.Info(
		fmt.Sprintf(
			"Sent message: %s",
			message.StringToPrint(),
		),
	)
	return nil
}

// Run starts the handler to read from and write to the serial port.
//
// Parameters:
//
// ctx: Context for managing cancellation and timeouts.
// stopFn: Function to call when stopping the handler.
//
// Returns:
//
// An error if any issue occurs during reading or writing.
func (h *DefaultHandler) Run(ctx context.Context, stopFn func()) error {
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

	// Reset the closed state
	h.closed.Store(false)

	// Initialize the outgoing messages channel
	h.outgoingMessagesCh = make(
		chan *OutgoingMessage,
		OutgoingMessagesChannelBufferSize,
	)
	defer h.close()

	// Reset received initialization message state
	h.receivedInitializationMessage = false

	// Reset received start message state
	h.receivedStartMessage = false

	// Reset received challenge
	h.receivedChallenge = internal.ChallengeNil
	h.challengeReady = make(chan struct{})
	h.notifyChallengeOnce = sync.Once{}

	// Reset received max motor speed value
	h.receivedMaxMotorSpeedValue = 0
	h.maxMotorSpeedValueReady = make(chan struct{})
	h.notifyMaxMotorSpeedValueOnce = sync.Once{}

	// Reset received max servo direction value
	h.receivedMaxServoDirectionValue = 0
	h.maxServoDirectionValueReady = make(chan struct{})
	h.notifyMaxServoDirectionValueOnce = sync.Once{}

	// Reset received BNO08X turns
	h.receivedBNO08XTurns = 0

	// Reset received BNO08X yaw degrees
	h.receivedBNO08XYawDegrees = 0.0

	h.mutex.Unlock()

	// Create a logger producer
	handlerLoggerProducer, err := h.logger.NewProducer(
		HandlerLoggerProducerTag,
	)
	if err != nil {
		return fmt.Errorf("failed to create logger producer: %w", err)
	}
	h.handlerLoggerProducer = handlerLoggerProducer
	defer h.handlerLoggerProducer.Close()

	return internallog.LogOnError(
		func() error {
			return h.runToWrap(ctx, stopFn)
		},
		h.handlerLoggerProducer,
	)
}

// NewSender returns a new sE instance associated with this DefaultHandler.
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

	// Check if the handler is already closed
	if h.IsClosed() {
		return nil, ErrHandlerClosed
	}

	// Increment the producer wait group counter
	h.wgSenders.Add(1)
	h.mutex.Unlock()

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
	if h.IsClosed() {
		h.mutex.Unlock()
		return
	}

	// Mark the handler as closed
	h.closed.Store(true)

	h.mutex.Unlock()

	// Wait for all registered producers to finish, then close channel.
	h.wgSenders.Wait()

	// Close the outgoing messages channel to signal no more messages will be sent.
	close(h.outgoingMessagesCh)

	// Reset the producer wait group
	h.wgSenders = sync.WaitGroup{}
}

// IsClosed returns true if the outgoing messages channel has been closed.
//
// Returns:
//
// True if the outgoing messages channel is closed, otherwise false.
func (h *DefaultHandler) IsClosed() bool {
	return h.closed.Load()
}

// ReceivedInitializationMessage returns true if the initialization message has been received.
//
// Returns:
//
// True if the initialization message has been received, otherwise false.
func (h *DefaultHandler) ReceivedInitializationMessage() bool {
	h.mutex.Lock()
	defer h.mutex.Unlock()
	return h.receivedInitializationMessage
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

// ReceivedMaxMotorSpeedValue returns the received maximum motor speed value.
//
// Returns:
//
// The received maximum motor speed value.
func (h *DefaultHandler) ReceivedMaxMotorSpeedValue() uint16 {
	h.mutex.Lock()
	defer h.mutex.Unlock()
	return h.receivedMaxMotorSpeedValue
}

// ReceivedMaxServoDirectionValue returns the received maximum servo direction value.
//
// Returns:
//
// The received maximum servo direction value.
func (h *DefaultHandler) ReceivedMaxServoDirectionValue() uint16 {
	h.mutex.Lock()
	defer h.mutex.Unlock()
	return h.receivedMaxServoDirectionValue
}

// ReceivedBNO08XTurns returns the received BNO08X turns.
//
// Returns:
//
// The received BNO08X turns.
func (h *DefaultHandler) ReceivedBNO08XTurns() int {
	h.mutex.Lock()
	defer h.mutex.Unlock()
	return h.receivedBNO08XTurns
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
	case <-h.challengeReady:
		return h.ReceivedChallenge(), nil
	}
}

// WaitForMaxMotorSpeedValue waits until a max motor speed value message is received or the context is done.
//
// Parameters:
//
// ctx: The context to control cancellation and timeouts.
//
// Returns:
//
// The received max motor speed value or an error if the context is done before receiving it.
func (h *DefaultHandler) WaitForMaxMotorSpeedValue(ctx context.Context) (
	uint16,
	error,
) {
	if v := h.ReceivedMaxMotorSpeedValue(); v != 0 {
		return v, nil
	}
	select {
	case <-ctx.Done():
		return 0, ctx.Err()
	case <-h.maxMotorSpeedValueReady:
		return h.ReceivedMaxMotorSpeedValue(), nil
	}
}

// WaitForMaxServoDirectionValue waits until a max servo direction value message is received or the context is done.
//
// Parameters:
//
// ctx: The context to control cancellation and timeouts.
//
// Returns:
//
// The received max servo direction value or an error if the context is done before receiving it.
func (h *DefaultHandler) WaitForMaxServoDirectionValue(ctx context.Context) (
	uint16,
	error,
) {
	if v := h.ReceivedMaxServoDirectionValue(); v != 0 {
		return v, nil
	}
	select {
	case <-ctx.Done():
		return 0, ctx.Err()
	case <-h.maxServoDirectionValueReady:
		return h.ReceivedMaxServoDirectionValue(), nil
	}
}
