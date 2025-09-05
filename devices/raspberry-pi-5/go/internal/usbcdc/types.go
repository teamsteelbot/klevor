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
		outgoingMessagesCh             chan *OutgoingMessage
		logger                         internallog.Logger
		loggerProducer                 internallog.LoggerProducer
		isRunning                      atomic.Bool
		closed                         atomic.Bool
		mutex                          sync.Mutex
		wgSenders                      sync.WaitGroup
		baudRate                       int
		buffer                         []byte
		accumulatedBuffer              []byte
		receivedInitializationMessage  bool
		receivedStartMessage           bool
		receivedChallenge              internal.Challenge
		receivedMaxMotorSpeedValue     uint16
		receivedMaxServoDirectionValue uint16
		receivedBNO08XTurns            int
		receivedBNO08XYawDegrees       float64
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
//
// Returns:
//
// A pointer to a DefaultHandler instance
func NewDefaultHandler(baudRate int) *DefaultHandler {
	// Create a buffer for reading data
	buffer := make([]byte, BufferSize)

	// Create an accumulated buffer for storing data
	accumulatedBuffer := make([]byte, 0)

	return &DefaultHandler{
		baudRate:          baudRate,
		buffer:            buffer,
		accumulatedBuffer: accumulatedBuffer,
	}
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
		func() error {
			return internal.StopContextOnError(
				ctx,
				stopFn,
				func(ctx context.Context) error {
					return h.incomingMessagesHandler(ctx, port)
				},
			)
		},
	)

	// Call the outgoing messages handler
	g.Go(
		func() error {
			return internal.StopContextOnError(
				ctx, stopFn,
				func(ctx context.Context) error {
					return h.outgoingMessagesHandler(ctx, port)
				},
			)
		},
	)

	// Wait for both handlers to finish and return any error
	err = g.Wait()

	// Close the port
	if closeErr := port.Close(); closeErr != nil {
		h.loggerProducer.Warning(
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
	h.loggerProducer.Info("Waiting for initialization message...")
	for !h.receivedInitializationMessage {
		select {
		case <-ctx.Done():
			return ctx.Err()
		default:
			// Read data from the port
			h.readFromPort(port)

			// Process the data read
			for _, c := range h.accumulatedBuffer {
				if c == InitializationMessage {
					h.receivedInitializationMessage = true
					h.loggerProducer.Info("Received initialization message")
					break
				}
			}
		}
	}

	// Waiting for start message
	h.loggerProducer.Info("Waiting for start message...")
	for !h.receivedStartMessage {
		select {
		case <-ctx.Done():
			return ctx.Err()
		default:
			// Read incoming messages
			messages := h.readIncomingMessages(port)

			// Send each message to the incoming messages channel
			for _, msg := range messages {
				if msg.IsAnErrorMessage() {
					return fmt.Errorf("received error message: %s", msg.Content)
				} else if IncomingStartMessage.IsEqual(msg) {
					h.receivedStartMessage = true
					h.loggerProducer.Info("Received start message")

					// Send a confirmation message
					h.outgoingMessagesCh <- OutgoingOKMessage
					break
				}
			}
		}
	}

	// Wait for challenge message
	h.loggerProducer.Info("Waiting for challenge message...")
	for h.receivedChallenge == internal.ChallengeNil {
		select {
		case <-ctx.Done():
			return ctx.Err()
		default:
			// Read incoming messages
			messages := h.readIncomingMessages(port)

			// Send each message to the incoming messages channel
			for _, msg := range messages {
				if msg.IsAnErrorMessage() {
					return fmt.Errorf("received error message: %s", msg.Content)
				} else if msg.IsAChallengeMessage() {
					challenge, err := internal.ChallengeFromString(msg.Content)
					if err != nil {
						return fmt.Errorf("failed to parse challenge: %w", err)
					}
					h.receivedChallenge = challenge
					h.loggerProducer.Info(
						fmt.Sprintf(
							"Received challenge message: %s",
							msg.String(),
						),
					)

					// Send a confirmation message
					h.outgoingMessagesCh <- OutgoingOKMessage
					break
				}
			}
		}
	}

	for {
		select {
		case <-ctx.Done():
			return ctx.Err()
		default:
			// Read incoming messages
			messages := h.readIncomingMessages(port)

			// Send each message to the incoming messages channel
			for _, msg := range messages {
				// Check if it's an error message
				if msg.IsAnErrorMessage() {
					return fmt.Errorf("received error message: %s", msg.Content)
				} else if msg.Category == internalusbcdcenums.IncomingCategoryBNO08XYawDegrees {
					// Parse the BNO08X yaw degrees value
					if err := ralvarezdevgostringsconvert.ToFloat64(
						msg.Content,
						&h.receivedBNO08XYawDegrees,
					); err != nil {
						return fmt.Errorf(
							"failed to parse BNO08X yaw degrees: %w",
							err,
						)
					}

					// Log the received message
					h.loggerProducer.Info(
						fmt.Sprintf(
							"Received BNO08X yaw degrees message: %s",
							msg.String(),
						),
					)
				} else if msg.Category == internalusbcdcenums.IncomingCategoryBNO08XYawTurns {
					// Parse the BNO08X turns value
					if err := ralvarezdevgostringsconvert.ToInt(
						msg.Content,
						&h.receivedBNO08XTurns,
					); err != nil {
						return fmt.Errorf(
							"failed to parse BNO08X turns: %w",
							err,
						)
					}

					// Log the received message
					h.loggerProducer.Info(
						fmt.Sprintf(
							"Received BNO08X turns message: %s",
							msg.String(),
						),
					)
				} else if msg.Category == internalusbcdcenums.IncomingCategoryMaxMotorSpeedValue {
					// Parse the max motor speed value
					if err := ralvarezdevgostringsconvert.ToUint16(
						msg.Content,
						&h.receivedMaxMotorSpeedValue,
					); err != nil {
						return fmt.Errorf(
							"failed to parse max motor speed value: %w",
							err,
						)
					}

					// Log the received message
					h.loggerProducer.Info(
						fmt.Sprintf(
							"Received max motor speed value message: %s",
							msg.String(),
						),
					)
				} else if msg.Category == internalusbcdcenums.IncomingCategoryMaxServoDirectionValue {
					// Parse the max servo direction value
					if err := ralvarezdevgostringsconvert.ToUint16(
						msg.Content,
						&h.receivedMaxServoDirectionValue,
					); err != nil {
						return fmt.Errorf(
							"failed to parse max servo direction value: %w",
							err,
						)
					}

					// Log the received message
					h.loggerProducer.Info(
						fmt.Sprintf(
							"Received max servo direction value message: %s",
							msg.String(),
						),
					)
				} else {
					// Log any other received message
					h.loggerProducer.Info(
						fmt.Sprintf(
							"Received message: %s",
							msg.String(),
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
func (h *DefaultHandler) readFromPort(port serial.Port) {
	n, err := port.Read(h.buffer)
	if err != nil {
		h.loggerProducer.Warning(
			fmt.Sprintf(
				"An error occurred while reading from the serial port: %v",
				err,
			),
		)
	}
	if n == 0 {
		// Read can return 0 bytes
		return
	}

	// Process the data read
	h.accumulatedBuffer = append(
		h.accumulatedBuffer,
		h.buffer[:n]...,
	)
}

// readIncomingMessages reads incoming messages from the serial port.
//
// Parameters:
//
// port: The serial port to read messages from.
//
// Returns:
//
// A slice of IncomingMessage pointers.
func (h *DefaultHandler) readIncomingMessages(
	port serial.Port,
) []*IncomingMessage {
	// Read data from the port
	h.readFromPort(port)

	// Extract messages from the accumulated buffer
	messages, err := NewIncomingMessagesFromBuffer(&h.accumulatedBuffer)
	if err != nil {
		h.loggerProducer.Warning(
			fmt.Sprintf(
				"An error occurred while processing incoming messages: %v",
				err,
			),
		)
		return nil
	}

	return messages
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
	lastHeartbeatTime := time.Now()
	for {
		select {
		case <-ctx.Done():
			// Process any remaining messages before returning
			for outgoingMessage := range h.outgoingMessagesCh {
				if err := h.sendMessage(port, outgoingMessage); err != nil {
					return err
				}
			}

			// Send the final stop message
			if err := h.sendMessage(port, OutgoingStopMessage); err != nil {
				return err
			}

			initialTime := time.Now()
			for time.Since(initialTime) < StopTimeout {
				// Read any remaining incoming messages and check if they are stop confirmations
				incomingMessages := h.readIncomingMessages(port)

				for _, msg := range incomingMessages {
					if msg.IsEqual(IncomingOKMessage) {
						h.loggerProducer.Info("Received stop confirmation message")
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
		h.loggerProducer.Warning("Attempted to send a nil outgoing message")
		return nil
	}

	// Send the message to the port
	if _, err := port.Write([]byte(message.String())); err != nil {
		return fmt.Errorf(ErrFailedToSendMessage, err)
	}

	// Log the message sent
	h.loggerProducer.Info(
		fmt.Sprintf(
			"Sent message: %s",
			message.String(),
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

	h.mutex.Unlock()

	// Reset the closed state
	h.closed.Store(false)

	// Create a logger producer
	loggerProducer, err := h.logger.NewProducer(
		HandlerLoggerProducerTag,
	)
	if err != nil {
		return fmt.Errorf("failed to create logger producer: %w", err)
	}
	h.loggerProducer = loggerProducer
	defer h.loggerProducer.Close()

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

	// Reset received max motor speed value
	h.receivedMaxMotorSpeedValue = 0

	// Reset received max servo direction value
	h.receivedMaxServoDirectionValue = 0

	// Reset received BNO08X turns
	h.receivedBNO08XTurns = 0

	// Reset received BNO08X yaw degrees
	h.receivedBNO08XYawDegrees = 0.0

	return internallog.LogOnError(
		func() error {
			return h.runToWrap(ctx, stopFn)
		},
		h.loggerProducer,
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
	loggerProducer, err := NewDefaultSender(
		func(m *OutgoingMessage) {
			h.outgoingMessagesCh <- m
		},
		func() { h.wgSenders.Done() },
	)
	if err != nil {
		h.wgSenders.Done()
		return nil, err
	}
	return loggerProducer, nil
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
	return h.receivedInitializationMessage
}

// ReceivedStartMessage returns true if the start message has been received.
//
// Returns:
//
// True if the start message has been received, otherwise false.
func (h *DefaultHandler) ReceivedStartMessage() bool {
	return h.receivedStartMessage
}

// ReceivedChallenge returns the received challenge.
//
// Returns:
//
// The received challenge.
func (h *DefaultHandler) ReceivedChallenge() internal.Challenge {
	return h.receivedChallenge
}

// ReceivedMaxMotorSpeedValue returns the received maximum motor speed value.
//
// Returns:
//
// The received maximum motor speed value.
func (h *DefaultHandler) ReceivedMaxMotorSpeedValue() uint16 {
	return h.receivedMaxMotorSpeedValue
}

// ReceivedMaxServoDirectionValue returns the received maximum servo direction value.
//
// Returns:
//
// The received maximum servo direction value.
func (h *DefaultHandler) ReceivedMaxServoDirectionValue() uint16 {
	return h.receivedMaxServoDirectionValue
}

// ReceivedBNO08XTurns returns the received BNO08X turns.
//
// Returns:
//
// The received BNO08X turns.
func (h *DefaultHandler) ReceivedBNO08XTurns() int {
	return h.receivedBNO08XTurns
}

// ReceivedBNO08XYawDegrees returns the received BNO08X yaw degrees.
//
// Returns:
//
// The received BNO08X yaw degrees.
func (h *DefaultHandler) ReceivedBNO08XYawDegrees() float64 {
	return h.receivedBNO08XYawDegrees
}
