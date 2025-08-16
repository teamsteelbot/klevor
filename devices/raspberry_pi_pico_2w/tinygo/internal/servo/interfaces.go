package servo

type (
	// Handler is the interface to handle servo operations
	Handler interface {
		SetAngle(angle uint16) error
		GetAngle() (uint16, error)
		SetAngleRelativeToCenter(angle uint16) error
		IsAngleCentered() bool
		SetAngleToCenter() error
		SetToAngleRight(angle uint16) error
		SetToAngleLeft(angle uint16) error
	}
)
