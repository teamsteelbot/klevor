package usbcdc

import (
	"errors"
)

const (
	ErrUnknownOutgoingCategory              = "unknown outgoing category: 0x%02X"
	ErrUnknownIncomingCategory              = "unknown incoming category: 0x%02X"
	ErrUnknownIncomingStatus                = "unknown incoming status: 0x%02X"
	ErrUnknownOutgoingStatus                = "unknown outgoing status: 0x%02X"
	ErrDataLengthMismatchForOutgoingMessage = "data length mismatch for outgoing message of category 0x%02X: expected %d, got %d"
	ErrFailedToSendMessage                   = "failed to send message of category 0x%02X: %v"
)

var (
	ErrNilHandler                               = errors.New("handler cannot be nil")
	ErrNilBuffer                                = errors.New("buffer cannot be nil")
	ErrHandlerAlreadyRunning                    = errors.New("handler is already running")
	ErrFailedToListPorts                        = errors.New("failed to list ports")
	ErrNoPortsFound                             = errors.New("no ports found")
	ErrPortNotFound                             = errors.New("port not found")
	ErrNilSendFunction                          = errors.New("nil send function")
	ErrNilCloseFunction                         = errors.New("nil close function")
	ErrSenderAlreadyClosed                      = errors.New("sender is already closed")
	ErrHandlerClosed                            = errors.New("handler is closed")
	ErrOutgoingMessagesChannelClosedAheadOfTime = errors.New("outgoing messages channel closed ahead of time")
	ErrIncomingMessageWithoutContent            = errors.New("incoming message without content")
	ErrNilOutgoingCategory                      = errors.New("outgoing category cannot be nil")
	ErrNilIncomingCategory                      = errors.New("incoming category cannot be nil")
	ErrNilOutgoingStatus                        = errors.New("outgoing status cannot be nil")
	ErrNilIncomingStatus                        = errors.New("incoming status cannot be nil")
	ErrNilCalculatedTurns                       = errors.New("calculated turns cannot be nil")
	ErrHandlerNotRunning                        = errors.New("handler is not running")
)
