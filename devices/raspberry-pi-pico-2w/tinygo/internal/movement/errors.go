package movement

import (
	tinygoerrors "github.com/ralvarezdev/tinygo-errors"
)

const (
	// ErrorCodeMovementStartNumber is the starting number for movement-related error codes.
	ErrorCodeMovementStartNumber uint16 = 30
)

const (
	ErrorCodeMovementNilHandler tinygoerrors.ErrorCode = tinygoerrors.ErrorCode(iota + ErrorCodeMovementStartNumber)
)
