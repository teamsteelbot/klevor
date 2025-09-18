package cyw43439

import (
	tinygoerrors "github.com/ralvarezdev/tinygo-errors"
)

const (
	// ErrorCodeCyw43439StartNumber is the starting number for CYW43439-related error codes.
	ErrorCodeCyw43439StartNumber uint16 = 10
)

const (
	ErrorCodeCyw43439NilDevice tinygoerrors.ErrorCode = tinygoerrors.ErrorCode(iota + ErrorCodeCyw43439StartNumber)
	ErrorCodeCyw43439FailedToInitialize
)
