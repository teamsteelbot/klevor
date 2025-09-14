package _switch

import (
	tinygotypes "github.com/ralvarezdev/tinygo-types"
)

const (
	// ErrorCodeSwitchStartNumber is the starting number for switch-related error codes.
	ErrorCodeSwitchStartNumber uint16 = 40
)

const (
	ErrorCodeSwitchNilOnEventFunction tinygotypes.ErrorCode = tinygotypes.ErrorCode(iota + ErrorCodeSwitchStartNumber)
)