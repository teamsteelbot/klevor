package onboard

import (
	"time"

	internalcyw43439 "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/cyw43439"
	internalled "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/led"
	soypatcyw43439 "github.com/soypat/cyw43439"
)

type (
	// DefaultHandler is the default implementation to manage the onboard LED of the Raspberry Pi Pico 2W.
	DefaultHandler struct {
		device *soypatcyw43439.Device
		state  bool
	}
)

// NewDefaultHandler creates a new instance of DefaultHandler for the onboard LED.
//
// Parameters:
//
// device: The CYW43439 device instance.
//
// Returns:
//
// An instance of DefaultHandler
func NewDefaultHandler(device *soypatcyw43439.Device) (*DefaultHandler, error) {
	if device == nil {
		return nil, internalcyw43439.ErrNilDevice
	}

	return &DefaultHandler{
		device,
		false,
	}, nil
}

// Setup initializes the onboard LED pin.
func (h *DefaultHandler) Setup() {}

// SetOn sets the LED to the on state.
func (h *DefaultHandler) SetOn() {
	_ = internalcyw43439.Device.GPIOSet(0, true)
	h.state = true
}

// SetOff sets the LED to the off state.
func (h *DefaultHandler) SetOff() {
	_ = internalcyw43439.Device.GPIOSet(0, false)
	h.state = false
}

// IsOn checks if the LED is currently on.
//
// Returns:
//
// True if the LED is on, otherwise false.
func (h *DefaultHandler) IsOn() bool {
	return h.state
}

// IsOff checks if the LED is currently off.
//
// Returns:
//
// True if the LED is off, otherwise false.
func (h *DefaultHandler) IsOff() bool {
	return !h.state
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
func (h *DefaultHandler) Blink(times int, delay time.Duration) error {
	// Validate the number of times to blink
	if times == 0 {
		return nil // No blinking needed
	}
	if times < 0 {
		return internalled.ErrNegativeBlinkCount
	}

	// Validate the delay duration
	if delay < 0 {
		return internalled.ErrNegativeDelayDuration
	}

	for _ = range times {
		h.SetOn()
		time.Sleep(delay)
		h.SetOff()
		time.Sleep(delay)
	}
	return nil
}
