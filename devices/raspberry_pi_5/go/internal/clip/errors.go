package clip

import (
	"errors"
)

var (
	ErrNilLineHandler    = errors.New("line handler cannot be nil")
	ErrNilPositiveLabels = errors.New("positive labels cannot be nil")
)
