package pilot

import (
	"errors"
)

var (
	ErrInvalidMotorDirection        = errors.New("invalid motor direction")
	ErrInvalidServoDirection        = errors.New("invalid servo direction")
	ErrNilRPLiDARMeasures           = errors.New("rplidar measures cannot be nil")
	ErrNotImplemented               = errors.New("not implemented")
	ErrHandlerAlreadyRunning        = errors.New("handler is already running")
	ErrMaxMotorSpeedValueNotSet     = errors.New("max motor speed value not set")
	ErrMaxServoDirectionValueNotSet = errors.New("max servo direction value not set")
	ErrNilQuaternion                = errors.New("nil quaternion provided")
)
