package escmotor

type (
	// ESCMotor is the interface to handle ESC (Electronic Speed Controller) motor operations
	ESCMotor interface {
		GetSpeed() int
		SetSpeed(speed uint16, isForward bool) error
		Stop() error
		GoForward(speed uint16) error
		GoBackward(speed uint16) error
	}
)
