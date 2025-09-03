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

const (
	filePerm = 0o644
	dirPerm  = 0o755
)

type (
	// DefaultLoggerProducer is the default LoggerProducer implementation for messages with different severity levels
	DefaultLoggerProducer struct {
		sendFn func(*Message)
		closed atomic.Bool
		once   sync.Once
		doneFn func()
		tag    string
		debug  bool
	}

	// DefaultLogger is the default Logger implementation to handle writing log messages to a file.
	DefaultLogger struct {
		ch     chan *Message
		wgProd sync.WaitGroup
		once   sync.Once
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
// doneFn: Function to call when done.
// tag: Optional tag to identify the logger instance.
// generateUniqueTag: Whether to generate a unique tag for the logger instance.
// debug: Flag to indicate if the logger is in debug mode.
//
// Returns:
//
// A pointer to a DefaultLoggerProducer instance or an error if the parameters are invalid.
func NewDefaultLoggerProducer(
	sendFn func(*Message),
	doneFn func(),
	tag *string,
	generateUniqueTag bool,
	debug bool,
) (*DefaultLoggerProducer, error) {
	// Check if the sendFn is nil
	if sendFn == nil {
		return nil, ErrNilSendFunction
	}

	// Check if the doneFn is nil
	if doneFn == nil {
		return nil, ErrNilDoneFunction
	}

	// Generate a unique tag if required
	if generateUniqueTag || tag == nil {
		// Generate a UUID to ensure uniqueness
		uniqueID, err := ralvarezdevgocryptouuid.NewUUIDv4()
		if err != nil {
			return nil, err
		}

		if tag != nil {
			*tag = fmt.Sprintf("%s_%s", *tag, uniqueID)
		} else {
			tag = new(string)
			*tag = fmt.Sprintf("Logger_%s", uniqueID)
		}
	}

	// Create a new DefaultLoggerProducer instance
	producer := &DefaultLoggerProducer{
		sendFn: sendFn,
		doneFn: doneFn,
		tag:    *tag,
		debug:  debug,
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
	message := NewMessage(category, content, &l.tag)

	// Send the message if the logger is not closed
	if l.Closed() {
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

// Done signals that the logger is done and performs cleanup.
func (l *DefaultLoggerProducer) Done() {
	l.once.Do(
		func() {
			// Send a final debug message if in debug mode
			l.Debug("Logger producer done")

			// Mark the logger as closed
			l.closed.Store(true)

			// Call the done function to signal completion
			l.doneFn()
		},
	)
}

// Closed returns true if the logger producer has been closed.
//
// Returns:
//
// True if the logger producer is closed, otherwise false.
func (l *DefaultLoggerProducer) Closed() bool {
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
func (w *DefaultLogger) Run(ctx context.Context) error {
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
	if err = writeLine(WriterStartedMessage); err != nil {
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
		case msg, ok := <-w.ch:
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
// tag: Optional tag to identify the logger instance.
// generateUniqueTag: Whether to generate a unique tag for the logger instance.
//
// Returns:
//
// A pointer to a LoggerProducer instance or an error if the parameters are invalid.
func (w *DefaultLogger) NewProducer(
	tag *string,
	generateUniqueTag bool,
) (LoggerProducer, error) {
	w.mutex.Lock()

	// Check if the logger is already closed
	if w.Closed() {
		return nil, ErrLoggerClosed
	}

	// Increment the producer wait group counter
	w.wgProd.Add(1)
	w.mutex.Unlock()

	// Create and return a new DefaultLoggerProducer instance
	producer, err := NewDefaultLoggerProducer(
		func(m *Message) {
			w.ch <- m
		},
		func() { w.wgProd.Done() },
		tag,
		generateUniqueTag,
		w.debug,
	)
	if err != nil {
		w.wgProd.Done()
		return nil, err
	}
	return producer, nil
}

// Close signals no more producers will send; safe to call multiple times.
func (w *DefaultLogger) Close() {
	w.once.Do(
		func() {
			// Mark the logger as closed
			w.mutex.Lock()
			w.closed.Store(true)
			w.mutex.Unlock()

			// Wait for all registered producers to finish, then close channel.
			w.wgProd.Wait()

			// Close the messages channel to signal no more messages will be sent.
			close(w.ch)
		},
	)
}

// Closed returns true if the logger channel has been closed.
//
// Returns:
//
// True if the logger channel is closed, otherwise false.
func (w *DefaultLogger) Closed() bool {
	return w.closed.Load()
}
