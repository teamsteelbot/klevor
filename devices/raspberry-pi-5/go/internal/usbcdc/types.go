package usbcdc

import (
	"context"
	"fmt"
	"sync"
	"sync/atomic"

	internallog "github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal/log"
	internalrplidar "github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal/rplidar"
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
		incomingMessagesCh chan *IncomingMessage
		outgoingMessagesCh chan *OutgoingMessage
		logger             internallog.Logger
		loggerProducer     internallog.LoggerProducer
		isRunning          atomic.Bool
		closed             atomic.Bool
		mutex              sync.Mutex
		wgSenders          sync.WaitGroup
		baudRate           int
		buffer             []byte
		accumulatedBuffer  []byte
		accumulatedBytes   int
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

// SendStopMessage sends a stop message through USB CDC.
func (s *DefaultSender) SendStopMessage() error {
	return s.SendMessage(OutgoingStopMessage)
}

// SendHeartbeatMessage sends a heartbeat message through USB CDC.
func (s *DefaultSender) SendHeartbeatMessage() error {
	return s.SendMessage(OutgoingHeartbeatMessage)
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

// GetIncomingMessagesChannel returns the channel to receive incoming messages.
//
// Returns:
//
// A read-only channel of IncomingMessage pointers.
func (h *DefaultHandler) GetIncomingMessagesChannel() <-chan *IncomingMessage {
	h.mutex.Lock()
	defer h.mutex.Unlock()
	return h.incomingMessagesCh
}

// runToWrap is the internal function to start the handler to read from and write to the serial port.
//
// Parameters:
//
// ctx: The context to control the lifecycle of the handler.
//
// Returns:
//
// An error if any issue occurs during reading or writing.
func (h *DefaultHandler) runToWrap(ctx context.Context) error {
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
			return h.incomingMessagesHandler(ctx, port)
		},
	)

	// Call the outgoing messages handler
	g.Go(
		func() error {
			return h.outgoingMessagesHandler(ctx, port)
		},
	)

	// Wait for both handlers to finish and return any error
	return g.Wait()
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
	for {
		select {
		case <-ctx.Done():
			return ctx.Err()
		default:
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
				continue
			}

			// Process the data read
			h.accumulatedBuffer = append(
				h.accumulatedBuffer,
				h.buffer[:n]...,
			)

			// Extract messages from the accumulated buffer
			messages, err := NewIncomingMessagesFromBuffer(&h.accumulatedBuffer)
			if err != nil {
				h.loggerProducer.Warning(
					fmt.Sprintf(
						"An error occurred while processing incoming messages: %v",
						err,
					),
				)
				continue
			}

			// Send each message to the incoming messages channel
			for _, msg := range messages {
				// Log the received message
				h.loggerProducer.Info(
					fmt.Sprintf(
						"Received message: %s",
						msg.String(),
					),
				)
				h.incomingMessagesCh <- &msg
			}
		}
	}
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
	for {
		select {
		case <-ctx.Done():
			// Process any remaining messages before returning
			for outgoingMessage := range h.outgoingMessagesCh {
				if err := h.sendMessage(port, outgoingMessage); err != nil {
					return err
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
//
// Returns:
//
// An error if any issue occurs during reading or writing.
func (h *DefaultHandler) Run(ctx context.Context) error {
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

	// Initialize the incoming messages channel
	h.incomingMessagesCh = make(
		chan *IncomingMessage,
		IncomingMessagesChannelBufferSize,
	)
	defer close(h.incomingMessagesCh)

	// Initialize the outgoing messages channel
	h.outgoingMessagesCh = make(
		chan *OutgoingMessage,
		OutgoingMessagesChannelBufferSize,
	)
	defer h.close()

	return internallog.LogOnError(
		func() error {
			return h.runToWrap(ctx)
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
