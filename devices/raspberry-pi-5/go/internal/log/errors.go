package log

import (
	"errors"
)

var (
	ErrNilWriterMessagesChannel = errors.New("writer messages channel cannot be nil")
	ErrNilSendFunction          = errors.New("send function cannot be nil")
	ErrNilCloseFunction         = errors.New("close function cannot be nil")
	ErrLoggerClosed             = errors.New("logger is closed")
	ErrNilLogger                = errors.New("logger cannot be nil")
)
