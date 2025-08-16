package led

import (
	"errors"
)

var (
	ErrNilHandler            = errors.New("led handler cannot be nil")
	ErrNegativeBlinkCount    = errors.New("times cannot be negative")
	ErrNegativeDelayDuration = errors.New("delay cannot be negative")
)
