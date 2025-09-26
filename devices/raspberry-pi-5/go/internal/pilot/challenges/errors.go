package challenges

import (
	"errors"
)

var (
	ErrInvalidMotorDirection               = errors.New("invalid motor direction")
	ErrInvalidServoDirection               = errors.New("invalid servo direction")
	ErrNotImplemented                      = errors.New("not implemented")
	ErrDidNotReceiveServoAngleStartMessage = errors.New("did not receive servo angle start message")
	ErrDidNotReceiveMotorSpeedStartMessage = errors.New("did not receive motor speed start message")
	ErrNilService                          = errors.New("service cannot be nil")
	ErrNoCardinalDirections                = errors.New("cardinal directions cannot be nil")
	ErrNilDirection                        = errors.New("direction cannot be nil")
	ErrNilLast90DegreeTurns                = errors.New("last 90 degree turns cannot be nil")
	ErrNilIsTurning                        = errors.New("is turning cannot be nil")
	ErrNilLastTurningTime                  = errors.New("last turning time cannot be nil")
	ErrServiceAlreadyRunning               = errors.New("service is already running")
	ErrNilUSBCDCSender                     = errors.New("usb-cdc sender cannot be nil")
	ErrNilIsObjectAvoidanceInProgress      = errors.New("is object avoidance in progress cannot be nil")
)
