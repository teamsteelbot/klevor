package main

import (
	"time"

	"github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal"
	internalledonboard "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/led/onboard"
	internalservo "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/servo"
	tinygoerrors "github.com/ralvarezdev/tinygo-errors"
)

var (
	// failedToServoAngleToLeftMessage is the message printed when setting the servo angle to left fails
	failedToServoAngleToLeftMessage = []byte("Failed to set servo angle to left:")

	// failedToServoAngleToRightMessage is the message printed when setting the servo angle to right fails
	failedToServoAngleToRightMessage = []byte("Failed to set servo angle to right:")
	
	// failedToServoAngleToCenterMessage is the message printed when setting the servo angle to center fails
	failedToServoAngleToCenterMessage = []byte("Failed to set servo angle to center:")

	// failedToSetServoAngleMessage is the message printed when setting the servo angle fails
	failedToSetServoAngleMessage = []byte("Failed to set servo angle:")
)

func main() {
	for {
		// Wait 5 seconds before starting the test
		time.Sleep(5 * time.Second)

		// Turn on the LED
		internalledonboard.OnBoardHandler.SetOn()

		// Start testing the servo to the right
		var angle uint16
		for angle = 0; angle <= 90; angle += 1 {
			if err := internalservo.ServoHandler.SetAngleToRight(
				angle,
			); err != tinygoerrors.ErrorCodeNil {
				internal.Logger.ErrorMessageWithErrorCode(failedToServoAngleToRightMessage, err, true)
				return
			}
			time.Sleep(50 * time.Millisecond)
		}

		// Center the servo for a while
		if err := internalservo.ServoHandler.SetAngleToCenter(); err != tinygoerrors.ErrorCodeNil {
			internal.Logger.ErrorMessageWithErrorCode(failedToServoAngleToCenterMessage, err, true)
			return
		}
		time.Sleep(2 * time.Second)

		// Start testing the servo to the left
		for angle = 0; angle <= 90; angle += 1 {
			if err := internalservo.ServoHandler.SetAngleToLeft(
				angle,
			); err != tinygoerrors.ErrorCodeNil {
				internal.Logger.ErrorMessageWithErrorCode(failedToServoAngleToLeftMessage, err, true)
				return
			}
			time.Sleep(50 * time.Millisecond)
		}

		// Center the servo
		if err := internalservo.ServoHandler.SetAngleToCenter(); err != tinygoerrors.ErrorCodeNil {
			internal.Logger.ErrorMessageWithErrorCode(failedToServoAngleToCenterMessage, err, true)
			return
		}
		time.Sleep(2 * time.Second)

		// Test servo full range
		for angle = 0; angle <= 180; angle += 1 {
			if err := internalservo.ServoHandler.SetAngle(angle); err != tinygoerrors.ErrorCodeNil {
				internal.Logger.ErrorMessageWithErrorCode(failedToSetServoAngleMessage, err, true)
				return
			}
			time.Sleep(50 * time.Millisecond)
		}

		// Center the servo
		if err := internalservo.ServoHandler.SetAngleToCenter(); err != tinygoerrors.ErrorCodeNil {
			internal.Logger.ErrorMessageWithErrorCode(failedToServoAngleToCenterMessage, err, true)
			return
		}

		// Turn off the LED
		internalledonboard.OnBoardHandler.SetOff()
	}
}
