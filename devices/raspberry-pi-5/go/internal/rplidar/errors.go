package rplidar

import (
	"errors"
)

var (
	ErrNilHandler            = errors.New("handler cannot be nil")
	ErrNilLineHandler        = errors.New("line handler cannot be nil")
	ErrHandlerAlreadyRunning = errors.New("handler is already running")
)
