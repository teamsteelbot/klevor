package main

import (
	"time"

	"github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal"
	internalescmotor "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/escmotor"
	internalledonboard "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/led/onboard"
	tinygoerrors "github.com/ralvarezdev/tinygo-errors"
)

var (
	// failedToStopMotorMessage is the message printed when stopping the motor fails
	failedToStopMotorMessage = []byte("Failed to stop motor:")

	// failedToSetMotorSpeedMessage is the message printed when setting the motor speed fails
	failedToSetMotorSpeedMessage = []byte("Failed to set motor speed:")
)

// stopOnError stops the motor and exits the program if there is an error.
//
// Parameters:
//
// err: The error to be checked.
func stopOnError(err tinygoerrors.ErrorCode) {
	if err != tinygoerrors.ErrorCodeNil {
		if stopErr := internalescmotor.ESCMotorHandler.Stop(); stopErr != tinygoerrors.ErrorCodeNil {
			internal.Logger.ErrorMessageWithErrorCode(failedToStopMotorMessage, stopErr, true)
		}
		internal.Logger.ErrorMessageWithErrorCode(failedToSetMotorSpeedMessage, err, true)
		return
	}
}

func main() {
	for {
		// Wait 5 seconds before starting the test
		time.Sleep(5 * time.Second)

		// Turn on the LED
		internalledonboard.OnBoardHandler.SetOn()

		// Start testing the motor forward
		var speed uint16
		for speed = 0; speed <= 11; speed += 1 {
			stopOnError(internalescmotor.ESCMotorHandler.SafeSetSpeedForward(
				speed * 10,
			))
			time.Sleep(1 * time.Second)
		}

		// Stop the motor for a while
		stopOnError(internalescmotor.ESCMotorHandler.Stop())
		time.Sleep(1 * time.Second)

		// Start testing the motor backward
		for speed = 0; speed <= 11; speed += 1 {
			stopOnError(internalescmotor.ESCMotorHandler.SafeSetSpeedBackward(
				speed * 10,
			))
			time.Sleep(1 * time.Second)
		}

		// Stop the motor
		stopOnError(internalescmotor.ESCMotorHandler.Stop())
		time.Sleep(1 * time.Second)

		// Turn off the LED
		internalledonboard.OnBoardHandler.SetOff()
	}
}
