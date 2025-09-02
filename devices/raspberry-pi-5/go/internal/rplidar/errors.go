package rplidar

import (
	"errors"
)

var (
	ErrNilRotationCompletedCh = errors.New("rotation completed channel cannot be nil")
	ErrNilLineHandler         = errors.New("line handler cannot be nil")
)
