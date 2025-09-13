package log

import (
	goconcurrentlogger "github.com/ralvarezdev/go-concurrent-logger"
)

// NewDefaultLogger creates a new default logger instance.
//
// Parameters:
//
// debug: A boolean indicating if debug logging is enabled
//
// Returns:
//
// A pointer to the DefaultLogger instance and an error if any
func NewDefaultLogger(debug bool) (*goconcurrentlogger.DefaultLogger, error) {
	return goconcurrentlogger.NewDefaultLogger(
		FilePath,
		GracefulShutdownTimeout,
		TimestampFormat,
		ChannelBufferSize,
		FileBufferSize,
		HandlerLoggerTag,
		debug,
	)
}
