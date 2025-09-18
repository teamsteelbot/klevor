package main

import (
	"time"

	"github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal"
	internalledonboard "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/led/onboard"
	internalservo "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/servo"
	tinygoerrors "github.com/ralvarezdev/tinygo-errors"
)

var (
	// failedToServoAngleToCenterMessage is the message printed when setting the servo angle to center fails
	failedToServoAngleToCenterMessage = []byte("Failed to set servo angle to center:")

	// failedToSetServoAngleMessage is the message printed when setting the servo angle fails
	failedToSetServoAngleMessage = []byte("Failed to set servo angle:")
)

// centerOnError centers the servo and exits the program if there is an error.
//
// Parameters:
//
// err: The error to be checked.
func centerOnError(err tinygoerrors.ErrorCode) {
	if err != tinygoerrors.ErrorCodeNil {
		if centerErr := internalservo.ServoHandler.SetAngleToCenter(); centerErr != tinygoerrors.ErrorCodeNil {
			internal.Logger.ErrorMessageWithErrorCode(
				failedToServoAngleToCenterMessage,
				centerErr,
				true,
			)
		}
		internal.Logger.ErrorMessageWithErrorCode(
			failedToSetServoAngleMessage,
			err,
			true,
		)
		return
	}
}

func main() {
	for {
		// Wait 5 seconds before starting the test
		time.Sleep(5 * time.Second)

		// Turn on the LED
		internalledonboard.OnBoardHandler.SetOn()

		// Start testing the servo to the right
		centerOnError(
			internalservo.ServoHandler.SafeSetAngleToRight(
				internalservo.MaxAngle,
			),
		)
		time.Sleep(1 * time.Second)

		// Center the servo for a while
		centerOnError(internalservo.ServoHandler.SetAngleToCenter())
		time.Sleep(1 * time.Second)

		// Start testing the servo to the left
		centerOnError(
			internalservo.ServoHandler.SafeSetAngleToLeft(
				internalservo.MaxAngle,
			),
		)
		time.Sleep(1 * time.Second)

		// Center the servo
		centerOnError(internalservo.ServoHandler.SetAngleToCenter())
		time.Sleep(1 * time.Second)

		// Turn off the LED
		internalledonboard.OnBoardHandler.SetOff()
	}
}
