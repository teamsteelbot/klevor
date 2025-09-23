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
			internal.Logger.ErrorMessageWithErrorCode(
				failedToStopMotorMessage,
				stopErr,
				true,
			)
		}
		internal.Logger.ErrorMessageWithErrorCode(
			failedToSetMotorSpeedMessage,
			err,
			true,
		)
		return
	}
}

func main() {
	// Wait 5 seconds before starting the test
	time.Sleep(5 * time.Second)

		
	for {
		// Turn on the LED
		internalledonboard.OnBoardHandler.SetOn()

		// Start testing the motor forward
		stopOnError(
			internalescmotor.ESCMotorHandler.SetSpeedForward(
				internalescmotor.MaxForwardSpeed,
			),
		)
		time.Sleep(100 * time.Millisecond)

		// Stop the motor for a while
		// stopOnError(internalescmotor.ESCMotorHandler.Stop())

		// Start testing the motor backward
		stopOnError(
			internalescmotor.ESCMotorHandler.SetSpeedBackward(
				internalescmotor.MaxBackwardSpeed,
			),
		)
		time.Sleep(100 * time.Millisecond)

		// Stop the motor
		// stopOnError(internalescmotor.ESCMotorHandler.Stop())

		// Turn off the LED
		internalledonboard.OnBoardHandler.SetOff()
	}
}
