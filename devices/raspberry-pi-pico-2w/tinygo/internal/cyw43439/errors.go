package cyw43439

import (
	tinygotypes "github.com/ralvarezdev/tinygo-types"
)

const (
	// ErrorCodeCyw43439StartNumber is the starting number for CYW43439-related error codes.
	ErrorCodeCyw43439StartNumber uint16 = 10
)

const (
	ErrorCodeCyw43439NilDevice tinygotypes.ErrorCode = tinygotypes.ErrorCode(iota + ErrorCodeCyw43439StartNumber)
	ErrorCodeCyw43439FailedToInitialize
)