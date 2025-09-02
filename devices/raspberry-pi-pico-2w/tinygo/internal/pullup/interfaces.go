package pullup

type (
	// Handler is the interface to handle pull-up resistor operations
	Handler interface {
		Setup()
		IsHigh() bool
		IsLow() bool
		IsOpen() bool
		IsShorted() bool
	}
)
