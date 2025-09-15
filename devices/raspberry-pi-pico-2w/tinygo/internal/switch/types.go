package _switch

import (
	"time"

	tinygopullup "github.com/ralvarezdev/tinygo-pullup"
	tinygoerrors "github.com/ralvarezdev/tinygo-errors"
)

type (
	// DefaultHandler is the default implementation of the Handler interface for managing the switch state.
	DefaultHandler struct {
		tinygopullup.Handler
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
	pullUpHandler tinygopullup.Handler,
	interval time.Duration,
) (*DefaultHandler, tinygoerrors.ErrorCode) {
	// Validate parameters
	if pullUpHandler == nil {
		return nil, tinygopullup.ErrorCodePullUpResistorNilHandler
	}

	return &DefaultHandler{
		pullUpHandler,
		interval,
	}, tinygoerrors.ErrorCodeNil
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
func (d *DefaultHandler) Wait(onEvent func() tinygoerrors.ErrorCode) tinygoerrors.ErrorCode {
	if onEvent == nil {
		return ErrorCodeSwitchNilOnEventFunction
	}

	// Check if the switch is already pressed
	for d.IsShorted() {
		time.Sleep(d.interval)
	}

	// Wait for the switch to be pressed
	for d.IsOpen() {
		time.Sleep(d.interval)
	}

	// Call the onEvent function
	return onEvent()
}
