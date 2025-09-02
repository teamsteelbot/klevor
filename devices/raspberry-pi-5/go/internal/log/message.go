package log

import (
	"fmt"
	"time"
)

type (
	// Message is the struct to handle log messages
	Message struct {
		Category      Category
		Content       string
		Tag           *string
		formattedTime string
	}
)

// NewMessage creates a new Message instance.
//
// Parameters:
//
// category: Category of the log message.
// content: Content of the log message.
// tag: Optional tag for the log message.
//
// Returns:
//
// A pointer to a Message instance.
func NewMessage(category Category, content string, tag *string) *Message {
	return &Message{
		category,
		content,
		tag,
		time.Now().Format(TimestampFormat),
	}
}

// String returns the representation of the log message.
//
// Returns:
//
// The formatted log message
func (m *Message) String() string {
	if m.Tag != nil {
		return fmt.Sprintf(
			"[%s] [%s] %s: %s",
			m.formattedTime,
			*m.Tag,
			m.Category.String(),
			m.Content,
		)
	}
	return fmt.Sprintf(
		"[%s] %s: %s",
		m.formattedTime,
		m.Category.String(),
		m.Content,
	)
}
