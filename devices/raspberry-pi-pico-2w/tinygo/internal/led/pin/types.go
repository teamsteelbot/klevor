package pin

import (
	"time"

	"machine"

	internalled "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/led"
	tinygoerrors "github.com/ralvarezdev/tinygo-errors"
)

type (
	// DefaultHandler is the default implementation to manage a LED connected to the Raspberry Pi Pico 2W.
	DefaultHandler struct {
		ledPin machine.Pin
	}
)

// NewDefaultHandler creates a new instance of DefaultHandler with the specified LED pin.
//
// Parameters:
//
// ledPin: The GPIO number where the LED is connected.
//
// Returns:
//
// An instance of DefaultHandler
func NewDefaultHandler(ledPin int) *DefaultHandler {
	return &DefaultHandler{
		machine.Pin(ledPin),
	}
}

// Setup initializes the LED pin as an output pin and sets it to the off state.
func (h *DefaultHandler) Setup() {
	h.ledPin.Configure(machine.PinConfig{Mode: machine.PinOutput})
	h.SetOff()
}

// SetOn sets the LED to the on state.
func (h *DefaultHandler) SetOn() {
	h.ledPin.High()
}

// SetOff sets the LED to the off state.
func (h *DefaultHandler) SetOff() {
	h.ledPin.Low()
}

// IsOn checks if the LED is currently on.
//
// Returns:
//
// True if the LED is on, otherwise false.
func (h *DefaultHandler) IsOn() bool {
	return h.ledPin.Get()
}

// IsOff checks if the LED is currently off.
//
// Returns:
//
// True if the LED is off, otherwise false.
func (h *DefaultHandler) IsOff() bool {
	return !h.ledPin.Get()
}

// Toggle changes the state of the LED from on to off or off to on.
func (h *DefaultHandler) Toggle() {
	if h.IsOn() {
		h.SetOff()
	} else {
		h.SetOn()
	}
}

// Blink makes the LED blink a specified number of times with a delay.
//
// Parameters:
//
// times: The number of times to blink the LED.
// delay: The duration to wait between turning the LED on and off.
//
// Returns:
//
// An error if the blink operation fails, otherwise nil.
func (h *DefaultHandler) Blink(times int, delay time.Duration) tinygoerrors.ErrorCode {
	// Validate the number of times to blink
	if times == 0 {
		return tinygoerrors.ErrorCodeNil // No blinking needed
	}
	if times < 0 {
		return internalled.ErrorCodeLEDNegativeBlinkCount
	}

	// Validate the delay duration
	if delay < 0 {
		return internalled.ErrorCodeLEDNegativeDelayDuration
	}

	for _ = range times {
		h.SetOn()
		time.Sleep(delay)
		h.SetOff()
		time.Sleep(delay)
	}
	return tinygoerrors.ErrorCodeNil
}
