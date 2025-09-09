package pullup

import (
	tinygotypes "github.com/ralvarezdev/tinygo-types"
	"github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal"
)


const (
	ErrorCodePullUpResistorNilHandler = tinygotypes.ErrorCode(iota + internal.ErrorCodePullUpResistorStartNumber)
)
