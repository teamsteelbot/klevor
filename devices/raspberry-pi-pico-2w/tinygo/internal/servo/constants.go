package servo

import (
	"machine"
	"os"

	"github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal"
	internalmovement "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/movement"
	tinygoservo "github.com/ralvarezdev/tinygo-servo"
	tinygotypes "github.com/ralvarezdev/tinygo-types"
)

const (
	// CenterAngle is the angle that represents the center position of the servo motors.
	CenterAngle uint16 = 90

	// MaxAngle is the maximum angle for the servo motors.
	MaxAngle uint16 = 15

	// IsDirectionInverted indicates if the servo direction is inverted.
	IsDirectionInverted bool = true

	// PWMFrequency is the frequency of the PWM signal used to control the servo motors.
	PWMFrequency uint16 = 330

	// MinPulseWidth is the minimum pulse width in microseconds for the servo motors.
	MinPulseWidth uint16 = 500

	// MaxPulseWidth is the maximum pulse width in microseconds for the servo motors.
	MaxPulseWidth uint16 = 2500
)

var (
	// ServoHandler is the default servo handler using the Raspberry Pi Pico 2W's PWM1 and GPIO2.
	ServoHandler tinygoservo.Handler

	// failedToInitializeServoMessage is the message printed when servo initialization fails
	failedToInitializeServoMessage = []byte("Failed to initialize Servo Handler:")
)

func init() {
	servoHandler, err := tinygoservo.NewDefaultHandler(
		machine.PWM2,
		machine.GPIO5,
		nil,
		internalmovement.Handler.IsEnabled,
		PWMFrequency,
		MinPulseWidth,
		MaxPulseWidth,
		CenterAngle,
		MaxAngle,
		nil, // internal.Logger
	)
	if err != tinygotypes.ErrorCodeNil {
		internal.Logger.ErrorMessageWithErrorCode(failedToInitializeServoMessage, err)
		os.Exit(1)
	}
	ServoHandler = servoHandler
}
