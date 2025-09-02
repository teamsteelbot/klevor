package servo

import (
	"errors"
)

const (
	ErrSendingDebugServoAngleMessage = "error sending debug servo angle message: %w"
	ErrInvalidAngle                  = "angle must be between %d and %d degrees, got %d"
	ErrAngleOutOfRange               = "angle must be between %d and %d degrees (actuation range), got %d"
)

var (
	ErrNilOptions = errors.New("servo options handler cannot be nil")
)
