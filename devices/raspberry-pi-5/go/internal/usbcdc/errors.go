package usbcdc

import (
	"errors"
)

var (
	ErrHandlerAlreadyRunning = errors.New("handler is already running")
	ErrFailedToListPorts     = errors.New("failed to list ports")
	ErrNoPortsFound          = errors.New("no ports found")
	ErrPortNotFound          = errors.New("port not found")
	ErrNilSendFunction       = errors.New("nil send function")
	ErrNilCloseFunction      = errors.New("nil close function")
	ErrSenderAlreadyClosed   = errors.New("sender is already closed")
	ErrHandlerClosed         = errors.New("handler is closed")
)
