package pilot

import (
	"errors"
)

var (
	ErrHandlerAlreadyRunning = errors.New("handler is already running")
)
