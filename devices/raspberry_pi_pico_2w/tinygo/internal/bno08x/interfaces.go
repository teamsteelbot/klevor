package bno08x

type (
	// Handler is the interface for the BNO08x sensor.
	Handler interface {
		Setup() error
		Update() error
		GetYawDegrees() float64
		GetPitchDegrees() float64
		GetRollDegrees() float64
	}
)
