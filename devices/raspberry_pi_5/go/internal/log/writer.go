package log

import (
	"context"
	"fmt"
	"os"
)

type (
	// DefaultWriter is the default implementation to handle writing log messages to a file.
	DefaultWriter struct {
		messagesQueue <-chan *Message
		debug         bool
	}
)

// NewDefaultWriter creates a new DefaultWriter instance.
//
// Parameters:
//
// messagesQueue: Channel to receive log messages.
// debug: Flag to indicate if the writer is in debug mode.
//
// Returns:
//
// A pointer to a DefaultWriter instance.
func NewDefaultWriter(
	messagesQueue <-chan *Message,
	debug bool,
) (*DefaultWriter, error) {
	// Check if the messagesQueue is nil
	if messagesQueue == nil {
		return nil, ErrNilMessagesChannel
	}

	return &DefaultWriter{
		messagesQueue,
		debug,
	}, nil
}

// WriteReceivedMessages processes and writes all received messages to the log file until the messagesQueue is closed or the context is cancelled.
//
// Parameters:
//
// ctx: The context to control cancellation and timeouts.
//
// Returns:
//
// An error if any issues occur during message processing or file writing.
func (w *DefaultWriter) WriteReceivedMessages(ctx context.Context) error {
	// Open the log file in append mode
	file, err := os.OpenFile(
		FilePath,
		os.O_APPEND|os.O_CREATE|os.O_WRONLY,
		0644,
	)
	if err != nil {
		return err
	}
	defer func(file *os.File) {
		if err := file.Close(); err != nil {
			fmt.Printf("Error closing file: %v\n", err)
		}
	}(file)

	// Process messages from the channel
	for {
		select {
		case <-ctx.Done():
			// Log a message indicating that the context was cancelled
			if _, err = file.WriteString(ContextCancelledMessage.String() + "\n"); err != nil {
				return err
			}
			return ctx.Err()
		case msg, ok := <-w.messagesQueue:
			if !ok {
				// Channel is closed, exit the loop
				if _, err = file.WriteString(MessagesChannelClosedMessage.String() + "\n"); err != nil {
					return err
				}
				return nil
			}
			if msg == nil {
				// Log that a nil message was received
				if _, err = file.WriteString(NilMessageReceivedMessage.String() + "\n"); err != nil {
					return err
				}
				continue
			}
			if _, err = file.WriteString(msg.String() + "\n"); err != nil {
				return err
			}
		}
	}
}
