package main

import (
	"github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/led"
	"github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/usbcdc"
)

// SwitchOnEventFunction is a function type that defines the signature for event handling functions.
//
// Parameters:
//
//	usbCDChandler: A handler for USB CDC communication.
//	ledHandler: A handler for controlling an LED.
//
// Returns:
//
// An error if the initialization or message sending fails, otherwise nil.
func SwitchOnEventFunction(
	usbCDChandler usbcdc.Handler,
	ledHandler led.Handler,
) error {
	// Send initialization message
	if err := usbCDChandler.SendInitializationMessage(); err != nil {
		return err
	}

	// Send challenge message
	if err := usbCDChandler.SendChallengeMessage(); err != nil {
		return err
	}

	// Blink the LED if provided
	if ledHandler != nil {
		if err := ledHandler.Blink(
			led.DefaultBlinkTimes,
			led.DefaultBlinkDelay,
		); err != nil {
			return err
		}
	}
	return nil
}
