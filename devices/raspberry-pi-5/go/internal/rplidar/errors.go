package rplidar

import (
	"errors"
)

var (
	ErrNilLineHandler        = errors.New("line handler cannot be nil")
	ErrHandlerAlreadyRunning = errors.New("handler is already running")
)
