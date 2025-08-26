package bno08x

import (
	"errors"
)

var (
	ErrNilBNO08X     = errors.New("bno08x instance cannot be nil")
	ErrNilQuaternion = errors.New("quaternion data cannot be nil")
)
