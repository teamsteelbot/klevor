package enabler

import (
	"machine"

	internalpullup "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/pullup"
	tinygotypes "github.com/ralvarezdev/tinygo-types"
)

type (
	// DefaultHandler is the default implementation of the Handler interface.
	DefaultHandler struct {
		internalpullup.Handler
	}
)

// NewDefaultHandler creates a new default debug handler with the given pull-up handler.
//
// Parameters:
//
//	pullUpHandler: The pull-up handler to use
//
// Returns:
//
//	An instance of DefaultHandler, or an error if the pull-up handler is nil
func NewDefaultHandler(
	pullUpHandler internalpullup.Handler,
) (*DefaultHandler, tinygotypes.ErrorCode) {
	if pullUpHandler == nil {
		return nil, internalpullup.ErrorCodePullUpResistorNilHandler
	}

	return &DefaultHandler{
		pullUpHandler,
	}, tinygotypes.ErrorCodeNil
}

// NewDefaultHandlerFromPin creates a new default debug handler with a pull-up handler created from the given pin.
func NewDefaultHandlerFromPin(pin machine.Pin) *DefaultHandler {
	pullUpHandler := internalpullup.NewDefaultHandler(pin)

	return &DefaultHandler{
		pullUpHandler,
	}
}

// IsEnabled checks if the debug mode is enabled.
func (d *DefaultHandler) IsEnabled() bool {
	return d.IsShorted()
}

// IsDisabled checks if the debug mode is disabled.
func (d *DefaultHandler) IsDisabled() bool {
	return d.IsOpen()
}
