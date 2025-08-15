package challenge

import (
	"machine"

	"github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/challenge/enums"
)

var (
	// OutputPin is the GPIO pin configured as output
	OutputPin *machine.Pin

	// InputPin is the GPIO pin configured as input
	InputPin *machine.Pin
)

// SetupPins configures and returns the output and input pins based on the provided pin numbers.
//
// Parameters:
//
// outputPin: The GPIO pin to be used as the output pin.
// inputPin: The GPIO pin to be used as the input pin.
func SetupPins(outputPin, inputPin int) {
	OutputPin = &machine.Pin(outputPin)
	InputPin = &machine.Pin(inputPin)

	// Configure the output pin.
	(*OutputPin).Configure(machine.PinConfig{Mode: machine.PinOutput})

	// This pin will always be in a high state (3.3V).
	(*OutputPin).High()

	// Configure the input pin.
	(*InputPin).Configure(machine.PinConfig{Mode: machine.PinInput})
}

// SetupDefaultPins configures and returns the default output and input pins.
//
// Returns:
//
// The configured default output and input machine.Pin instances.
func SetupDefaultPins() {
	SetupPins(DefaultOutputPin, DefaultInputPin)
}

// ReadShortedPins reads the state of the input pin to determine if it is shorted to the output pin.
//
// Returns:
//
// An enums.Challenge indicating whether the pins are shorted or not.
func ReadShortedPins() enums.Challenge {
	return enums.ChallengeFromBoolean((*InputPin).Get())
}
