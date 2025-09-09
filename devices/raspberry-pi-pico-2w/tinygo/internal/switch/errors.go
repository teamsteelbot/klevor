package _switch

import (
	tinygotypes "github.com/ralvarezdev/tinygo-types"
	"github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal"
)

const (
	ErrorCodeSwitchNilOnEventFunction tinygotypes.ErrorCode = tinygotypes.ErrorCode(iota + internal.ErrorCodeSwitchStartNumber)
)