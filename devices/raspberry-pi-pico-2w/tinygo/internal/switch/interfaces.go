package _switch

import (
	tinygoerrors "github.com/ralvarezdev/tinygo-errors"
	tinygopullup "github.com/ralvarezdev/tinygo-pullup"
)

type (
	// Handler is the interface to manage the switch state.
	Handler interface {
		tinygopullup.Handler
		Wait(onEvent func() tinygoerrors.ErrorCode) tinygoerrors.ErrorCode
	}
)
