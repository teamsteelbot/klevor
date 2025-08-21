package _switch

import (
	"time"

	internalpullup "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/pullup"
)

type (
	// DefaultHandler is the default implementation of the Handler interface for managing the switch state.
	DefaultHandler struct {
		internalpullup.Handler
		interval time.Duration
	}
)

// NewDefaultHandler creates a new instance of DefaultHandler
//
// Parameters:
//
// pullUpHandler: The pull-up handler to use
// interval: The interval to wait for the switch to be pressed
//
// Returns:
//
// An instance of DefaultHandler, or an error if the pull-up handler is nil
func NewDefaultHandler(
	pullUpHandler internalpullup.Handler,
	interval time.Duration,
) (*DefaultHandler, error) {
	if pullUpHandler == nil {
		return nil, internalpullup.ErrNilPullUpHandler
	}

	return &DefaultHandler{
		pullUpHandler,
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
