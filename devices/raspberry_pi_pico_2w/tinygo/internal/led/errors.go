package led

import (
	"errors"
)

var (
	ErrNegativeBlinkCount    = errors.New("times cannot be negative")
	ErrNegativeDelayDuration = errors.New("delay cannot be negative")
)
