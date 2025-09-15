package main

import (
	"time"

	"github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal"
	internalescmotor "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/escmotor"
	internalledonboard "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/led/onboard"
	tinygoerrors "github.com/ralvarezdev/tinygo-errors"
)

var (
	// failedToSetMotorSpeedForwardMessage is the message printed when setting the motor speed forward fails
	failedToSetMotorSpeedForwardMessage = []byte("Failed to set motor speed forward:")

	// failedToSetMotorSpeedBackwardMessage is the message printed when setting the motor speed backward fails
	failedToSetMotorSpeedBackwardMessage = []byte("Failed to set motor speed backward:")

	// failedToStopMotorMessage is the message printed when stopping the motor fails
	failedToStopMotorMessage = []byte("Failed to stop motor:")

	// failedToSetMotorSpeedMessage is the message printed when setting the motor speed fails
	failedToSetMotorSpeedMessage = []byte("Failed to set motor speed:")
)

func main() {
	for {
		// Wait 5 seconds before starting the test
		time.Sleep(5 * time.Second)

		// Turn on the LED
		internalledonboard.OnBoardHandler.SetOn()

		// Start testing the motor forward
		var speed uint16
		for speed = 0; speed <= 100; speed += 1 {
			if err := internalescmotor.ESCMotorHandler.SetSpeedForward(
				speed,
			); err != tinygoerrors.ErrorCodeNil {
				internal.Logger.ErrorMessageWithErrorCode(failedToSetMotorSpeedForwardMessage, err, true)
				return
			}
			time.Sleep(20 * time.Millisecond)
		}

		// Stop the motor for a while
		if err := internalescmotor.ESCMotorHandler.Stop(); err != tinygoerrors.ErrorCodeNil {
			internal.Logger.ErrorMessageWithErrorCode(failedToStopMotorMessage, err, true)
			return
		}
		time.Sleep(2 * time.Second)

		// Start testing the motor backward
		for speed = 0; speed <= 100; speed += 1 {
			if err := internalescmotor.ESCMotorHandler.SetSpeedBackward(
				speed,
			); err != tinygoerrors.ErrorCodeNil {
				internal.Logger.ErrorMessageWithErrorCode(failedToSetMotorSpeedBackwardMessage, err, true)
				return
			}
			time.Sleep(20 * time.Millisecond)
		}

		// Stop the motor
		if err := internalescmotor.ESCMotorHandler.Stop(); err != tinygoerrors.ErrorCodeNil {
			internal.Logger.ErrorMessageWithErrorCode(failedToStopMotorMessage, err, true)
			return
		}

		// Turn off the LED
		internalledonboard.OnBoardHandler.SetOff()
	}
}
