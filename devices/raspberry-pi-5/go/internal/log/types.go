package log

import (
	"bufio"
	"context"
	"fmt"
	"os"
	"path/filepath"
	"sync"
	"sync/atomic"

	ralvarezdevgocryptouuid "github.com/ralvarezdev/go-crypto/uuid"
)

type (
	// DefaultLoggerProducer is the default LoggerProducer implementation for messages with different severity levels
	DefaultLoggerProducer struct {
		sendFn  func(*Message)
		closed  atomic.Bool
		closeFn func()
		tag     string
		mutex   sync.Mutex
		debug   bool
	}

	// DefaultLogger is the default Logger implementation to handle writing log messages to a file.
	DefaultLogger struct {
		ch     chan *Message
		wgProd sync.WaitGroup
		closed atomic.Bool
		mutex  sync.Mutex
		debug  bool
	}
)

// NewDefaultLoggerProducer creates a new DefaultLoggerProducer instance.
//
// Parameters:
//
// sendFn: Function to send messages.
// closeFn: Function to call when done.
// tag: Tag to identify the logger instance.
// debug: Flag to indicate if the logger is in debug mode.
//
// Returns:
//
// A pointer to a DefaultLoggerProducer instance or an error if the parameters are invalid.
func NewDefaultLoggerProducer(
	sendFn func(*Message),
	closeFn func(),
	tag string,
	debug bool,
) (*DefaultLoggerProducer, error) {
	// Check if the sendFn is nil
	if sendFn == nil {
		return nil, ErrNilSendFunction
	}

	// Check if the closeFn is nil
	if closeFn == nil {
		return nil, ErrNilCloseFunction
	}

	// Generate a unique tag if required
	if tag == "" {
		// Generate a UUID to ensure uniqueness
		uniqueID, err := ralvarezdevgocryptouuid.NewUUIDv4()
		if err != nil {
			return nil, err
		}
		tag = uniqueID
	}

	// Create a new DefaultLoggerProducer instance
	producer := &DefaultLoggerProducer{
		sendFn:  sendFn,
		closeFn: closeFn,
		tag:     tag,
		debug:   debug,
	}

	// Log the initialization if a tag is provided
	producer.Debug("Initializing new DefaultLoggerProducer")

	return producer, nil
}

// Log logs a message with the specified content and category.
//
// Parameters:
//
// content: The content of the log message.
// category: The category of the log message.
func (l *DefaultLoggerProducer) Log(content string, category Category) {
	// Create a message object
	message := NewMessage(category, content, l.tag)

	// Send the message if the logger is not closed
	if l.IsClosed() {
		fmt.Println("Logger is closed. Cannot log message: ", message.String())
		return
	}
	l.sendFn(message)
}

// Info logs an informational message.
//
// Parameters:
//
// content: The content of the informational message.
func (l *DefaultLoggerProducer) Info(content string) {
	l.Log(content, CategoryInfo)
}

// Error logs an error message.
//
// Parameters:
//
// content: The content of the error message.
func (l *DefaultLoggerProducer) Error(content string) {
	l.Log(content, CategoryError)
}

// Warning logs a warning message.
//
// Parameters:
//
// content: The content of the warning message.
func (l *DefaultLoggerProducer) Warning(content string) {
	l.Log(content, CategoryWarning)
}

// Debug logs a debug message if the logger is in debug mode.
//
// Parameters:
//
// content: The content of the debug message.
func (l *DefaultLoggerProducer) Debug(content string) {
	if l.debug {
		l.Log(content, CategoryDebug)
	}
}

// Close signals that the logger is done and performs cleanup.
func (l *DefaultLoggerProducer) Close() {
	l.mutex.Lock()

	// Check if already closed to prevent multiple calls
	if l.IsClosed() {
		l.mutex.Unlock()
		return
	}

	// Send a final debug message if in debug mode
	l.Debug("Closed")

	// Mark the logger as closed
	l.closed.Store(true)

	l.mutex.Unlock()

	// Call the close function to signal completion
	l.closeFn()
}

// IsClosed returns true if the logger producer has been closed.
//
// Returns:
//
// True if the logger producer is closed, otherwise false.
func (l *DefaultLoggerProducer) IsClosed() bool {
	return l.closed.Load()
}

// Tag returns the tag associated with the logger producer.
//
// Returns:
//
// The tag string.
func (l *DefaultLoggerProducer) Tag() string {
	return l.tag
}

// IsDebug returns true if the logger producer is in debug mode.
//
// Returns:
//
// True if the logger producer is in debug mode, otherwise false.
func (l *DefaultLoggerProducer) IsDebug() bool {
	return l.debug
}

// NewDefaultLogger creates a new DefaultLogger instance.
//
// Parameters:
//
// debug: Flag to indicate if the writer is in debug mode.
//
// Returns:
//
// A pointer to a DefaultLogger instance.
func NewDefaultLogger(
	debug bool,
) *DefaultLogger {
	return &DefaultLogger{
		ch:    make(chan *Message, ChannelBufferSize),
		debug: debug,
	}
}

// Run processes and writes all received messages to the log file until the channel is closed or the context is cancelled.
//
// Parameters:
//
// ctx: The context to control cancellation and timeouts.
//
// Returns:
//
// An error if any issues occur during message processing or file writing.
func (l *DefaultLogger) Run(ctx context.Context) error {
	// Check if the logger is already closed
	if l.IsClosed() {
		return ErrLoggerClosed
	}

	// Ensure parent directory exists
	logDir := filepath.Dir(FilePath)
	if err := os.MkdirAll(logDir, dirPerm); err != nil {
		return fmt.Errorf("creating log directory %s: %w", logDir, err)
	}

	// Open the log file in append mode
	file, err := os.OpenFile(
		FilePath,
		os.O_APPEND|os.O_CREATE|os.O_WRONLY,
		filePerm,
	)
	if err != nil {
		return err
	}
	defer func(file *os.File) {
		if err := file.Close(); err != nil {
			fmt.Printf("Error closing file: %v\n", err)
		}
	}(file)

	// Create a buffered writer for efficient file writing
	buf := bufio.NewWriterSize(file, FileBufferSize)
	defer func(buf *bufio.Writer) {
		err := buf.Flush()
		if err != nil {
			fmt.Printf("Error flushing buffer: %v\n", err)
		}
	}(buf)

	// Create a helper function to write a message to the buffer
	writeLine := func(m *Message) error {
		if m == nil {
			m = NilMessageReceivedMessage
		}
		if _, err := buf.WriteString(m.String() + "\n"); err != nil {
			return err
		}
		return nil
	}

	// Log a message indicating that the writer has started
	if err = writeLine(LoggerStartedMessage); err != nil {
		return err
	}

	// Process messages from the channel
	for {
		select {
		case <-ctx.Done():
			// Log a message indicating that the context was cancelled
			_ = writeLine(ContextCancelledMessage)
			_ = buf.Flush()
			return ctx.Err()
		case msg, ok := <-l.ch:
			if !ok {
				// Channel is closed, exit the loop
				_ = writeLine(MessagesChannelClosedMessage)
				_ = buf.Flush()
				return nil
			}
			if err = writeLine(msg); err != nil {
				return err
			}
			_ = buf.Flush()
		}
	}
}

// NewProducer returns a new LoggerProducer instance associated with this DefaultLogger.
//
// Parameters:
//
// tag: Tag to identify the logger instance.
//
// Returns:
//
// A pointer to a LoggerProducer instance or an error if the parameters are invalid.
func (l *DefaultLogger) NewProducer(
	tag string,
) (LoggerProducer, error) {
	l.mutex.Lock()

	// Check if the logger is already closed
	if l.IsClosed() {
		return nil, ErrLoggerClosed
	}

	// Increment the producer wait group counter
	l.wgProd.Add(1)
	l.mutex.Unlock()

	// Create and return a new DefaultLoggerProducer instance
	loggerProducer, err := NewDefaultLoggerProducer(
		func(m *Message) {
			l.ch <- m
		},
		func() { l.wgProd.Done() },
		tag,
		l.debug,
	)
	if err != nil {
		l.wgProd.Done()
		return nil, err
	}
	return loggerProducer, nil
}

// Close signals no more producers will send; safe to call multiple times.
func (l *DefaultLogger) Close() {
	l.mutex.Lock()

	// Check if the logger is already closed
	if l.IsClosed() {
		l.mutex.Unlock()
		return
	}

	// Mark the logger as closed
	l.closed.Store(true)

	l.mutex.Unlock()

	// Wait for all registered producers to finish, then close channel.
	l.wgProd.Wait()

	// Close the messages channel to signal no more messages will be sent.
	close(l.ch)
}

// IsClosed returns true if the logger channel has been closed.
//
// Returns:
//
// True if the logger channel is closed, otherwise false.
func (l *DefaultLogger) IsClosed() bool {
	return l.closed.Load()
}

// IsDebug returns true if the logger is in debug mode.
//
// Returns:
//
// True if the logger is in debug mode, otherwise false.
func (l *DefaultLogger) IsDebug() bool {
	return l.debug
}

// Reset resets the logger to its initial state.
func (l *DefaultLogger) Reset() {
	l.mutex.Lock()
	defer l.mutex.Unlock()

	// Only reset if the logger is closed
	if !l.IsClosed() {
		return
	}

	// Reset the closed state
	l.closed.Store(false)

	// Reinitialize the messages channel
	l.ch = make(chan *Message, ChannelBufferSize)

	// Reset the producer wait group
	l.wgProd = sync.WaitGroup{}
}
