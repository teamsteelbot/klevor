package debug

import (
	"errors"
)

var (
	ErrNilHandler = errors.New("debug handler cannot be nil")
)
