package escmotor

type (
	// ESCMotor is the interface to handle ESC (Electronic Speed Controller) motor operations
	ESCMotor interface {
		GetSpeed() int
		SetSpeed(speed int)
		Stop()
		GoForward(speed uint)
		GoBackward(speed uint)
	}
)
