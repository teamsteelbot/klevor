package servo

import (
	tinygotypes "github.com/ralvarezdev/tinygo-types"
	"github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal"
)

const (
	ErrorCodeServoNilOptions tinygotypes.ErrorCode = tinygotypes.ErrorCode(iota + internal.ErrorCodeServoStartNumber)
	ErrorCodeServoFailedToInitializeServo 
	ErrorCodeServoInvalidAngleValue
	ErrorCodeServoAngleOutOfRange
	ErrorCodeServoAngleBelowMinPulseWidth
	ErrorCodeServoAngleAboveMaxPulseWidth
	ErrorCodeServoFailedToSendDebugServoAngleMessage
	ErrorCodeServoUnknownAngleCategory
	ErrorCodeServoFailedToSetServoAngle
)