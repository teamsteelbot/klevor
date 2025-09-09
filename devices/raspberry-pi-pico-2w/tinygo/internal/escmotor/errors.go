package escmotor

import (
	tinygotypes "github.com/ralvarezdev/tinygo-types"
	"github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal"
)

const (
	ErrorCodeESCMotorNilOptions tinygotypes.ErrorCode = tinygotypes.ErrorCode(iota + internal.ErrorCodeESCMotorStartNumber)
	ErrorCodeESCMotorFailedToInitializeServo 
	ErrorCodeESCMotorInvalidMotorSpeedValue
	ErrorCodeESCMotorSpeedOutOfRange
	ErrorCodeESCMotorSpeedBelowMinPulseWidth
	ErrorCodeESCMotorSpeedAboveMaxPulseWidth
	ErrorCodeESCMotorFailedToSendDebugMotorSpeedMessage
	ErrorCodeESCMotorUnknownMotorSpeedCategory
)
