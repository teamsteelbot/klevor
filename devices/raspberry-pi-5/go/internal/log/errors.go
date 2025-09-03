package log

import (
	"errors"
)

var (
	ErrNilWriterMessagesChannel = errors.New("writer messages channel cannot be nil")
	ErrNilSendFunction          = errors.New("send function cannot be nil")
	ErrNilDoneFunction          = errors.New("done function cannot be nil")
	ErrLoggerClosed             = errors.New("logger is closed")
)
