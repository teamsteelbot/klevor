package log

import (
	"context"
)

type (
	// LoggerProducer is an interface for logging messages with different severity levels
	LoggerProducer interface {
		Log(content string, category Category)
		Info(content string)
		Error(content string)
		Warning(content string)
		Debug(content string)
		Done()
		Closed() bool
		Tag() string
	}

	// Logger is an interface for writing log messages to a file
	Logger interface {
		NewProducer() LoggerProducer
		Run(ctx context.Context) error
		Close()
		Closed() bool
	}
)
