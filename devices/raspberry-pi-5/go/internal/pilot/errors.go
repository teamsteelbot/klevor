package pilot

import (
	"errors"
)

var (
	ErrInvalidMotorDirection               = errors.New("invalid motor direction")
	ErrInvalidServoDirection               = errors.New("invalid servo direction")
	ErrNilRPLiDARMeasures                  = errors.New("rplidar measures cannot be nil")
	ErrNotImplemented                      = errors.New("not implemented")
	ErrHandlerAlreadyRunning               = errors.New("handler is already running")
	ErrMaxMotorSpeedValueNotSet            = errors.New("max motor speed value not set")
	ErrMaxServoAngleValueNotSet            = errors.New("max servo value value not set")
	ErrDidNotReceiveServoAngleStartMessage = errors.New("did not receive servo angle start message")
	ErrDidNotReceiveMotorSpeedStartMessage = errors.New("did not receive motor speed start message")
)
