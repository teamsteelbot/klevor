package _switch

import (
	tinygopullup "github.com/ralvarezdev/tinygo-pullup"
	tinygoerrors "github.com/ralvarezdev/tinygo-errors"
)

type (
	// Handler is the interface to manage the switch state.
	Handler interface {
		tinygopullup.Handler
		Wait(onEvent func() tinygoerrors.ErrorCode) tinygoerrors.ErrorCode
	}
)
