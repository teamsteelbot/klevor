package log

import (
	goconcurrentlogger "github.com/ralvarezdev/go-concurrent-logger"
)

// NewDefaultLogger creates a new default logger instance.
//
// Returns:
//
// A pointer to the DefaultLogger instance and an error if any
func NewDefaultLogger() (*goconcurrentlogger.DefaultLogger, error) {
	return goconcurrentlogger.NewDefaultLogger(
		FilePath,
		GracefulShutdownTimeout,
		TimestampFormat,
		ChannelBufferSize,
		FileBufferSize,
		HandlerLoggerTag,
	)
}
