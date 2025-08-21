package servo

type (
	// Handler is the interface to handle servo operations
	Handler interface {
		SetAngle(angle uint16) error
		GetAngle() uint16
		SetAngleRelativeToCenter(relativeAngle int16) error
		IsAngleCentered() bool
		SetAngleToCenter() error
		SetAngleToRight(angle uint16) error
		SetAngleToLeft(angle uint16) error
	}
)
