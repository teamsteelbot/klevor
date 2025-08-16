package escmotor

type (
	// Handler is the interface to handle ESC (Electronic Speed Controller) motor operations
	Handler interface {
		GetSpeed() int16
		SetSpeed(speed uint16, isForward bool) error
		Stop() error
		SetSpeedForward(speed uint16) error
		SetSpeedBackward(speed uint16) error
	}
)
