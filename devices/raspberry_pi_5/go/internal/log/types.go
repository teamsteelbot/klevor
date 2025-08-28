package log

import (
	"fmt"

	ralvarezdevgocryptouuid "github.com/ralvarezdev/go-crypto/uuid"
)

type (
	// DefaultLogger is the default logger for messages with different severity levels
	DefaultLogger struct {
		writerMessagesChannel chan<- *Message
		tag                   string
		debug                 bool
	}
)

// NewDefaultLogger creates a new DefaultLogger instance.
//
// Parameters:
//
// writerMessagesChannel: Channel to send log messages.
// tag: Optional tag to identify the logger instance.
// generateUniqueTag: Whether to generate a unique tag for the logger instance.
// debug: Flag to indicate if the logger is in debug mode.
//
// Returns:
//
// A pointer to a DefaultLogger instance or an error if the writerMessagesChannel is nil.
func NewDefaultLogger(
	writerMessagesChannel chan<- *Message,
	tag *string,
	generateUniqueTag bool,
	debug bool,
) (*DefaultLogger, error) {
	// Check if the writerMessagesChannel is nil
	if writerMessagesChannel == nil {
		return nil, ErrNilWriterMessagesChannel
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

	// Create a new DefaultLogger instance
	logger := &DefaultLogger{
		writerMessagesChannel,
		*tag,
		debug,
	}

	// Log the initialization if a tag is provided
	logger.Debug("Initializing new Default")

	return logger, nil
}

// Log logs a message with the specified content and category.
//
// Parameters:
//
// content: The content of the log message.
// category: The category of the log message.
func (l *DefaultLogger) Log(content string, category Category) {
	// Create a message object
	msg := NewMessage(category, content, &l.tag)

	// Put the message in the channel
	l.writerMessagesChannel <- msg
}

// Info logs an informational message.
//
// Parameters:
//
// content: The content of the informational message.
func (l *DefaultLogger) Info(content string) {
	l.Log(content, CategoryInfo)
}

// Error logs an error message.
//
// Parameters:
//
// content: The content of the error message.
func (l *DefaultLogger) Error(content string) {
	l.Log(content, CategoryError)
}

// Warning logs a warning message.
//
// Parameters:
//
// content: The content of the warning message.
func (l *DefaultLogger) Warning(content string) {
	l.Log(content, CategoryWarning)
}

// Debug logs a debug message if the logger is in debug mode.
//
// Parameters:
//
// content: The content of the debug message.
func (l *DefaultLogger) Debug(content string) {
	if l.debug {
		l.Log(content, CategoryDebug)
	}
}
