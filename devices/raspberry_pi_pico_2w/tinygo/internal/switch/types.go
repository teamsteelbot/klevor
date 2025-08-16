package _switch

import (
	"time"

	"github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/pulldown"
)

type (
	// DefaultHandler is the default implementation of the Handler interface for managing the switch state.
	DefaultHandler struct {
		pulldown.Handler
		interval time.Duration
	}
)

// NewDefaultHandler creates a new instance of DefaultHandler
//
// Parameters:
//
// pullDownHandler: The pull-down handler to use
// interval: The interval to wait for the switch to be pressed
//
// Returns:
//
// An instance of DefaultHandler, or an error if the pull-down handler is nil
func NewDefaultHandler(
	pullDownHandler pulldown.Handler,
	interval time.Duration,
) (*DefaultHandler, error) {
	if pullDownHandler == nil {
		return nil, pulldown.ErrNilPullDownHandler
	}

	return &DefaultHandler{
		pullDownHandler,
		interval,
	}, nil
}

// Wait waits for the switch to be pressed
//
// Parameters:
//
// onEvent: The function to call when the switch is pressed
//
// Returns:
//
// An error if the wait fails
func (d *DefaultHandler) Wait(onEvent func()) error {
	if onEvent == nil {
		return ErrNilOnEventFunction
	}

	// Check if the switch is already pressed
	for d.IsShorted() {
		time.Sleep(d.interval)
	}

	// Wait for the switch to be pressed
	for d.IsOpen() {
		time.Sleep(d.interval)
	}

	go onEvent()
	return nil
}
