package log

import (
	"errors"
)

var (
	ErrNilSendFunction      = errors.New("send function cannot be nil")
	ErrNilCloseFunction     = errors.New("close function cannot be nil")
	ErrLoggerClosed         = errors.New("logger is closed")
	ErrNilLogger            = errors.New("logger cannot be nil")
	ErrLoggerAlreadyRunning = errors.New("logger is already running")
)
