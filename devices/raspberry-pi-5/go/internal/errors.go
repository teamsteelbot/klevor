package internal

import (
	"fmt"
)

const (
	ErrUnknownChallenge          = "unknown challenge with uint8 value: %#02X"
)

var (
	ErrNilChallenge = fmt.Errorf("challenge cannot be nil")
)
