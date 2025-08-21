package main

import (
	"fmt"
	"strings"
	"time"

	internaldebug "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/debug"
	internalledonboard "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/led/onboard"
	internalmovement "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/movement"
	internalservo "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/servo"
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

		// Start testing the servo to the right
		var angle uint16
		for angle = 0; angle <= 90; angle += 1 {
			if err := internalservo.ServoHandler.SetAngleToRight(
				angle,
			); err != nil {
				fmt.Println(err)
			}
			time.Sleep(50 * time.Millisecond)
		}

		// Center the servo for a while
		if err := internalservo.ServoHandler.SetAngleToCenter(); err != nil {
			fmt.Println(err)
		}
		time.Sleep(2 * time.Second)

		// Start testing the servo to the left
		for angle = 0; angle <= 90; angle += 1 {
			if err := internalservo.ServoHandler.SetAngleToLeft(
				angle,
			); err != nil {
				fmt.Println(err)
			}
			time.Sleep(50 * time.Millisecond)
		}

		// Center the servo
		if err := internalservo.ServoHandler.SetAngleToCenter(); err != nil {
			fmt.Println(err)
		}
		time.Sleep(2 * time.Second)

		// Test servo full range
		for angle = 0; angle <= 180; angle += 1 {
			if err := internalservo.ServoHandler.SetAngle(angle); err != nil {
				fmt.Println(err)
			}
			time.Sleep(50 * time.Millisecond)
		}

		// Center the servo
		if err := internalservo.ServoHandler.SetAngleToCenter(); err != nil {
			fmt.Println(err)
		}

		// Turn off the LED
		internalledonboard.OnBoardHandler.SetOff()
	}
}
