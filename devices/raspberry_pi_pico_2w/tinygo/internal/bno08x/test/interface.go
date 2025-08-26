package test

type (
	// BNO08XService is an interface to wrap the BNO08X implementation methods.
	BNO08XService interface {
		Acceleration() *[3]float64
		EulerDegrees() *[3]float64
	}
)
