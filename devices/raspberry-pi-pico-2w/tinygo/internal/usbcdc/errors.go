package usbcdc

import (
	"errors"
)

const (
	ErrConfirmationMessageTimeout = "confirmation message timeout exceeded for message: %s, after %f"
	ErrUnknownChallengeType       = "unknown challenge type: %s"
	ErrFailedReadingFromSerial    = "failed reading from serial: %w"
	ErrNilOutgoingCategory        = "outgoing message category cannot be nil or empty, got: %s"
	ErrFailedToSendChunkMessage   = "failed to send chunk message: %w"
	ErrFailedToSendMessage        = "failed to send message: %w"
	ErrFailedToSendEndCharacter   = "failed to send end character: %w"
	ErrFailedToConfigureUSBCDC    = "failed to configure USB CDC: %w"
)

var (
	ErrNilHandler         = errors.New("usb-cdc handler cannot be nil")
	ErrNilOutgoingMessage = errors.New("outgoing message cannot be nil")
	ErrNilIncomingMessage = errors.New("incoming message cannot be nil")
)
