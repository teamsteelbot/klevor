package _switch

import (
	internalled "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/led"
	internalusbcdc "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/usbcdc"
	tinygoerrors "github.com/ralvarezdev/tinygo-errors"
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
) func() tinygoerrors.ErrorCode {
	return func() tinygoerrors.ErrorCode {
		var err tinygoerrors.ErrorCode

		// Send start messages multiple times to ensure the host receives it
		for _ = range InitializationAttempts {
			// Send start message
			if err = usbCDChandler.SendStartMessage(); err == tinygoerrors.ErrorCodeNil {
				break
			}
		}
		if err != tinygoerrors.ErrorCodeNil {
			return err
		}

		// Send challenge messages multiple times to ensure the host receives it
		for _ = range InitializationAttempts {
			if err = usbCDChandler.SendChallengeMessage(); err == tinygoerrors.ErrorCodeNil {
				break
			}
		}
		if err != tinygoerrors.ErrorCodeNil {
			return err
		}

		// Blink the LED if provided
		if ledHandler != nil {
			ledHandler.Blink(
				internalled.DefaultBlinkTimes,
				internalled.DefaultBlinkDelay,
			)
		}
		return tinygoerrors.ErrorCodeNil
	}
}
