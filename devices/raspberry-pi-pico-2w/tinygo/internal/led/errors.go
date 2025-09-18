package led

import (
	tinygoerrors "github.com/ralvarezdev/tinygo-errors"
)

const (
	// ErrorCodeLEDStartNumber is the starting number for LED-related error codes.
	ErrorCodeLEDStartNumber uint16 = 20
)

const (
	ErrorCodeLEDNilHandler tinygoerrors.ErrorCode = tinygoerrors.ErrorCode(iota + ErrorCodeLEDStartNumber)
	ErrorCodeLEDNegativeBlinkCount
	ErrorCodeLEDNegativeDelayDuration
)
