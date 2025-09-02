package escmotor

import (
	"errors"
)

const (
	ErrSpeedBelowMinPulseWidth       = "speed below minimum pulse width, must be greater than or equal to %dus, which corresponds to a speed of %d, received %d"
	ErrSpeedAboveMaxPulseWidth       = "speed above maximum pulse width, must be less than or equal to %dus, which corresponds to a speed of %d, received %d"
	ErrSpeedOutOfRange               = "speed must be between -%d and %d, received %d"
	ErrSendingDebugMotorSpeedMessage = "error sending debug motor speed message: %w"
)

var (
	ErrNilOptions = errors.New("esc motor options cannot be nil")
)
