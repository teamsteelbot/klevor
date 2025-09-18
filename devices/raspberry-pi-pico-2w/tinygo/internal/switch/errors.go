package _switch

import (
	tinygoerrors "github.com/ralvarezdev/tinygo-errors"
)

const (
	// ErrorCodeSwitchStartNumber is the starting number for switch-related error codes.
	ErrorCodeSwitchStartNumber uint16 = 40
)

const (
	ErrorCodeSwitchNilOnEventFunction tinygoerrors.ErrorCode = tinygoerrors.ErrorCode(iota + ErrorCodeSwitchStartNumber)
)
