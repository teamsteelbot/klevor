package movement

import (
	tinygotypes "github.com/ralvarezdev/tinygo-types"
)

const (
	// ErrorCodeMovementStartNumber is the starting number for movement-related error codes.
	ErrorCodeMovementStartNumber uint16 = 30
)

const (
	ErrorCodeMovementNilHandler tinygotypes.ErrorCode = tinygotypes.ErrorCode(iota + ErrorCodeMovementStartNumber)
)
