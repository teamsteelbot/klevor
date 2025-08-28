package log

import (
	"errors"
)

var (
	ErrNilWriterMessagesChannel = errors.New("writer messages channel cannot be nil")
	ErrNilMessagesChannel       = errors.New("messages channel cannot be nil")
)
