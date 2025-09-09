package main

import (
	"time"

	internalledonboard "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/led/onboard"
	internalservo "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/servo"
	tinygotypes "github.com/ralvarezdev/tinygo-types"
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
			); err != tinygotypes.ErrorCodeNil {
				return
			}
			time.Sleep(50 * time.Millisecond)
		}

		// Center the servo for a while
		if err := internalservo.ServoHandler.SetAngleToCenter(); err != tinygotypes.ErrorCodeNil {
			return
		}
		time.Sleep(2 * time.Second)

		// Start testing the servo to the left
		for angle = 0; angle <= 90; angle += 1 {
			if err := internalservo.ServoHandler.SetAngleToLeft(
				angle,
			); err != tinygotypes.ErrorCodeNil {
				return
			}
			time.Sleep(50 * time.Millisecond)
		}

		// Center the servo
		if err := internalservo.ServoHandler.SetAngleToCenter(); err != tinygotypes.ErrorCodeNil {
			return
		}
		time.Sleep(2 * time.Second)

		// Test servo full range
		for angle = 0; angle <= 180; angle += 1 {
			if err := internalservo.ServoHandler.SetAngle(angle); err != tinygotypes.ErrorCodeNil {
				return
			}
			time.Sleep(50 * time.Millisecond)
		}

		// Center the servo
		if err := internalservo.ServoHandler.SetAngleToCenter(); err != tinygotypes.ErrorCodeNil {
			return
		}

		// Turn off the LED
		internalledonboard.OnBoardHandler.SetOff()
	}
}
