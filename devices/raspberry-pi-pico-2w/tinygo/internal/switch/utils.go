package _switch

import (
	internalled "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/led"
	internalusbcdc "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/usbcdc"
)

// SwitchOnEventGenerator returns a function that initializes USB CDC communication and provides visual feedback via an LED when the switch is pressed.
//
// Parameters:
//
//	usbCDChandler: A handler for USB CDC communication.
//	ledHandler: A handler for controlling an LED.
//
// Returns:
//
// A function that performs the initialization and LED blinking when called, or an error if any step fails.
func SwitchOnEventGenerator(
	usbCDChandler internalusbcdc.Handler,
	ledHandler internalled.Handler,
) func() error {
	return func() error {
		// Send initialization message
		if err := usbCDChandler.SendInitializationMessage(); err != nil {
			return err
		}

		// Send start message
		if err := usbCDChandler.SendStartMessage(); err != nil {
			return err
		}

		// Send challenge message
		if err := usbCDChandler.SendChallengeMessage(); err != nil {
			return err
		}

		// Blink the LED if provided
		if ledHandler != nil {
			if err := ledHandler.Blink(
				internalled.DefaultBlinkTimes,
				internalled.DefaultBlinkDelay,
			); err != nil {
				return err
			}
		}
		return nil
	}
}
