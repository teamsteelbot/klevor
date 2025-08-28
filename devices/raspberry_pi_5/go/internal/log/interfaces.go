package log

import (
	"context"
)

type (
	// Logger is an interface for logging messages with different severity levels
	Logger interface {
		GetUniqueTag(tag string) string
		Log(content string, category Category)
		Info(content string)
		Error(content string)
		Warning(content string)
		Debug(content string)
	}

	// Writer is an interface for writing log messages to a file
	Writer interface {
		WriteReceivedMessages(ctx context.Context) error
	}
)
