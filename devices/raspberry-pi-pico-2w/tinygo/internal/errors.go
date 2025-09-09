package internal

import (
	tinygotypes "github.com/ralvarezdev/tinygo-types"
)

const (
	// ErrorCodeGeneralStartNumber is the starting number for general error codes.
	ErrorCodeGeneralStartNumber uint16 = 1

	// ErrorCodeChallengeStartNumber is the starting number for challenge-related error codes.
	ErrorCodeChallengeStartNumber uint16 = 100

	// ErrorCodeCyw43439StartNumber is the starting number for CYW43439-related error codes.
	ErrorCodeCyw43439StartNumber uint16 = 200

	// ErrorCodeDebugStartNumber is the starting number for debug-related error codes.
	ErrorCodeDebugStartNumber uint16 = 300

	// ErrorCodeESCMotorStartNumber is the starting number for ESC motor-related error codes.
	ErrorCodeESCMotorStartNumber uint16 = 400

	// ErrorCodeLEDStartNumber is the starting number for LED-related error codes.
	ErrorCodeLEDStartNumber uint16 = 500

	// ErrorCodeMovementStartNumber is the starting number for movement-related error codes.
	ErrorCodeMovementStartNumber uint16 = 600

	// ErrorCodePullUpResistorStartNumber is the starting number for pull-up resistor-related error codes.
	ErrorCodePullUpResistorStartNumber uint16 = 700

	// ErrorCodeServoStartNumber is the starting number for servo-related error codes.
	ErrorCodeServoStartNumber uint16 = 800

	// ErrorCodeSwitchStartNumber is the starting number for switch-related error codes.
	ErrorCodeSwitchStartNumber uint16 = 900

	// ErrorCodeUSBCDCStartNumber is the starting number for USB CDC-related error codes.
	ErrorCodeUSBCDCStartNumber uint16 = 1000
)

const (
	ErrorCodeFailedToConfigurePWM tinygotypes.ErrorCode = tinygotypes.ErrorCode(iota + ErrorCodeGeneralStartNumber)
)
