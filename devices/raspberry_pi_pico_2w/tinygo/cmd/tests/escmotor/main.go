package main

import (
	"fmt"
	"strings"
	"time"

	internaldebug "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/debug"
	internalescmotor "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/escmotor"
	internalledonboard "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/led/onboard"
	internalmovement "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/movement"
)

func main() {
	spacer := strings.Repeat("-", 40)

	for {
		// Wait 5 seconds before starting the test
		time.Sleep(5 * time.Second)

		// Print movement and debug flag
		fmt.Printf(
			"\n%s\nMovement flag: %t\nDebug flag: %t\n%s\n",
			spacer,
			internalmovement.Handler.IsEnabled(),
			internaldebug.Handler.IsEnabled(),
			spacer,
		)

		// Turn on the LED
		internalledonboard.OnBoardHandler.SetOn()

		// Start testing the motor forward
		var speed uint16
		for speed = 0; speed <= 250; speed += 1 {
			if err := internalescmotor.ESCMotorHandler.SetSpeedForward(
				speed,
			); err != nil {
				fmt.Println(err)
			}
			time.Sleep(10 * time.Millisecond)
		}

		// Stop the motor for a while
		if err := internalescmotor.ESCMotorHandler.Stop(); err != nil {
			fmt.Println(err)
		}
		time.Sleep(2 * time.Second)

		// Start testing the motor backward
		for speed = 0; speed <= 250; speed += 1 {
			if err := internalescmotor.ESCMotorHandler.SetSpeedBackward(
				speed,
			); err != nil {
				fmt.Println(err)
			}
			time.Sleep(10 * time.Millisecond)
		}

		// Stop the motor
		if err := internalescmotor.ESCMotorHandler.Stop(); err != nil {
			fmt.Println(err)
		}

		// Turn off the LED
		internalledonboard.OnBoardHandler.SetOff()
	}
}
