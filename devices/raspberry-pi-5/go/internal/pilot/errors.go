package pilot

import (
	"errors"
)

var (
	ErrNilUSBCDCSender       = errors.New("usb-cdc sender cannot be nil")
	ErrAngleWidthMustBeOdd   = errors.New("angle width must be odd")
	ErrAngleWidthTooSmall    = errors.New("angle width must be greater than 0")
	ErrAngleWidthTooLarge    = errors.New("angle width must be less than 360 degrees")
	ErrInvalidMotorDirection = errors.New("invalid motor direction")
	ErrInvalidServoDirection = errors.New("invalid servo direction")
	ErrNilRPLiDARMeasures    = errors.New("rplidar measures cannot be nil")
	ErrNotImplemented        = errors.New("not implemented")
	ErrHandlerAlreadyRunning = errors.New("handler is already running")
)
