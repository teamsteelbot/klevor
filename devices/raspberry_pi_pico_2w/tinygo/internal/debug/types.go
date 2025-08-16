package debug

import (
	"github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/pulldown"
)

type (
	// DefaultHandler is the default implementation of the Handler interface.
	DefaultHandler struct {
		pulldown.Handler
	}
)

// NewDefaultHandler creates a new default debug handler with the given pull-down handler.
//
// Parameters:
//
//	pullDownHandler: The pull-down handler to use
//
// Returns:
//
//	An instance of DefaultHandler, or an error if the pull-down handler is nil
func NewDefaultHandler(
	pullDownHandler pulldown.Handler,
) (*DefaultHandler, error) {
	if pullDownHandler == nil {
		return nil, pulldown.ErrNilPullDownHandler
	}

	return &DefaultHandler{
		pullDownHandler,
	}, nil
}

// IsEnabled checks if the debug mode is enabled.
func (d *DefaultHandler) IsEnabled() bool {
	return d.IsShorted()
}

// IsDisabled checks if the debug mode is disabled.
func (d *DefaultHandler) IsDisabled() bool {
	return d.IsOpen()
}
