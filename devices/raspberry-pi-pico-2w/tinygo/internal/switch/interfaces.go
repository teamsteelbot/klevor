package _switch

import (
	tinygopullup "github.com/ralvarezdev/tinygo-pullup"
	tinygotypes "github.com/ralvarezdev/tinygo-types"
)

type (
	// Handler is the interface to manage the switch state.
	Handler interface {
		tinygopullup.Handler
		Wait(onEvent func() tinygotypes.ErrorCode) tinygotypes.ErrorCode
	}
)
