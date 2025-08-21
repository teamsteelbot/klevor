package pullup

import (
	"machine"
)

type (
	// DefaultHandler is the default implementation to handle pull-up resistor.
	DefaultHandler struct {
		inputPin machine.Pin
	}
)

// NewDefaultHandler creates a new instance of DefaultHandler
//
// Parameters:
//
// inputPin: The GPIO pin to be used as the input pin.
//
// Returns:
//
// An instance of DefaultHandler.
func NewDefaultHandler(inputPin machine.Pin) *DefaultHandler {
	return &DefaultHandler{
		inputPin,
	}
}

// Setup initializes the input pin for the DefaultHandler
func (d *DefaultHandler) Setup() {
	d.inputPin.Configure(machine.PinConfig{Mode: machine.PinInputPullup})
}

// IsHigh checks if the input pin is high.
//
// Returns:
//
// True if the input pin is high, otherwise false.
func (d *DefaultHandler) IsHigh() bool {
	return d.inputPin.Get()
}

// IsLow checks if the input pin is low.
//
// Returns:
//
// True if the input pin is low, otherwise false.
func (d *DefaultHandler) IsLow() bool {
	return !d.inputPin.Get()
}

// IsOpen checks if the input pin is open (not connected).
//
// Returns:
//
// True if the input pin is open, otherwise false.
func (d *DefaultHandler) IsOpen() bool {
	return d.IsHigh()
}

// IsShorted checks if the input pin is shorted (connected to ground).
//
// Returns:
//
// True if the input pin is shorted, otherwise false.
func (d *DefaultHandler) IsShorted() bool {
	return d.IsLow()
}
