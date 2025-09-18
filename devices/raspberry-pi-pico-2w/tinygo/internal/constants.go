package internal

import (
	tinygologger "github.com/ralvarezdev/tinygo-logger"
)

var (
	// LoggerBufferSize is the size of the logger buffer.
	LoggerBufferSize uint64 = 512

	// Logger is the default logger instance.
	Logger tinygologger.Logger = tinygologger.NewDefaultLogger(LoggerBufferSize)
)
