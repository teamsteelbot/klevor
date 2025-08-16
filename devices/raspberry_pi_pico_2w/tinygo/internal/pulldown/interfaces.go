package pulldown

type (
	// Handler is the interface to handle pull-down resistor operations
	Handler interface {
		Setup()
		IsHigh() bool
		IsLow() bool
		IsOpen() bool
		IsShorted() bool
	}
)
