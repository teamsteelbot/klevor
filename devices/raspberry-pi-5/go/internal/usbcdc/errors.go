package usbcdc

import (
	"errors"
)

const (
	ErrUnknownOutgoingCategory              = "unknown outgoing category: 0x%02X"
	ErrUnknownIncomingCategory              = "unknown incoming category: 0x%02X"
	ErrUnknownIncomingStatus                = "unknown incoming status: 0x%02X"
	ErrUnknownOutgoingStatus                = "unknown outgoing status: 0x%02X"
	ErrFailedToSendStartByte                = "failed to send start byte: %w"
	ErrFailedToSendCategoryByte             = "failed to send category byte: %w"
	ErrFailedToSendEndByte                  = "failed to send end byte: %w"
	ErrFailedToSendDataBytes                = "failed to send data bytes: %w"
	ErrDataLengthMismatchForOutgoingMessage = "data length mismatch for outgoing message of category 0x%02X: expected %d, got %d"
	ErrFailedToSendDataLengthByte           = "failed to send data length bytes: %w"
	ErrFailedToSendChecksumByte			  = "failed to send checksum byte: %w"
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
