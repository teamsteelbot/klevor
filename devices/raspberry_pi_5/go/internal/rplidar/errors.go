package rplidar

import (
	"errors"
)

var (
	ErrNilMeasuresMapChannel = errors.New("measures map channel cannot be nil")
	ErrNilLineHandler        = errors.New("line handler cannot be nil")
)
