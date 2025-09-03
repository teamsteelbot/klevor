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
		Close()
		IsClosed() bool
		Tag() string
		IsDebug() bool
	}

	// Logger is an interface for writing log messages to a file
	Logger interface {
		NewProducer(
			tag string,
		) (LoggerProducer, error)
		Run(ctx context.Context) error
		Close()
		IsClosed() bool
		IsDebug() bool
	}
)
