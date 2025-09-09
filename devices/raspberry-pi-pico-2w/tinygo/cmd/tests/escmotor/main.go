package main

import (
	"time"

	internalescmotor "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/escmotor"
	internalledonboard "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/led/onboard"
	tinygotypes "github.com/ralvarezdev/tinygo-types"
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
			); err != tinygotypes.ErrorCodeNil {
				return
			}
			time.Sleep(20 * time.Millisecond)
		}

		// Stop the motor for a while
		if err := internalescmotor.ESCMotorHandler.Stop(); err != tinygotypes.ErrorCodeNil {
			return
		}
		time.Sleep(2 * time.Second)

		// Start testing the motor backward
		for speed = 0; speed <= 100; speed += 1 {
			if err := internalescmotor.ESCMotorHandler.SetSpeedBackward(
				speed,
			); err != tinygotypes.ErrorCodeNil {
				return
			}
			time.Sleep(20 * time.Millisecond)
		}

		// Stop the motor
		if err := internalescmotor.ESCMotorHandler.Stop(); err != tinygotypes.ErrorCodeNil {
			return
		}

		// Turn off the LED
		internalledonboard.OnBoardHandler.SetOff()
	}
}
