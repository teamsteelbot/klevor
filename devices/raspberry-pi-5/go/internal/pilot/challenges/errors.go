package challenges

import (
	"errors"
)

var (
	ErrInvalidMotorDirection               = errors.New("invalid motor direction")
	ErrInvalidServoDirection               = errors.New("invalid servo direction")
	ErrNilRPLiDARMeasures                  = errors.New("rplidar measures cannot be nil")
	ErrNotImplemented                      = errors.New("not implemented")
	ErrDidNotReceiveServoAngleStartMessage = errors.New("did not receive servo angle start message")
	ErrDidNotReceiveMotorSpeedStartMessage = errors.New("did not receive motor speed start message")
	ErrNoSpaceToLeaveParking               = errors.New("no space to leave parking")
	ErrNilService                          = errors.New("service cannot be nil")
	ErrNoCardinalDirections 			  = errors.New("cardinal directions cannot be nil")
)
