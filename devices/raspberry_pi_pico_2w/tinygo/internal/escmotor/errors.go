package escmotor

const (
	ErrSpeedBelowMinPulseWidth       = "speed below minimum pulse width, must be greater than or equal to %dus, which corresponds to a speed of %d"
	ErrSpeedAboveMaxPulseWidth       = "speed above maximum pulse width, must be less than or equal to %dus, which corresponds to a speed of %d"
	ErrSendingDebugMotorSpeedMessage = "error sending debug motor speed message: %w"
)
