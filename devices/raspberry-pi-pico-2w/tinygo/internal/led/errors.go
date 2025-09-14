package led

import (
	tinygotypes "github.com/ralvarezdev/tinygo-types"
)

const (
	// ErrorCodeLEDStartNumber is the starting number for LED-related error codes.
	ErrorCodeLEDStartNumber uint16 = 20
)

const (
	ErrorCodeLEDNilHandler tinygotypes.ErrorCode = tinygotypes.ErrorCode(iota + ErrorCodeLEDStartNumber)
	ErrorCodeLEDNegativeBlinkCount
	ErrorCodeLEDNegativeDelayDuration
)