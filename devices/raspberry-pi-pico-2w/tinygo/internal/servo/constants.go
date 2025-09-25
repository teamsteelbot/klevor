package servo

import (
	"os"

	"machine"

	"github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal"
	internalmovement "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/movement"
	tinygoerrors "github.com/ralvarezdev/tinygo-errors"
	tinygoservo "github.com/ralvarezdev/tinygo-servo"
)

const (
	// ActuationRange is the actuation range of the servo motors in degrees.
	ActuationRange uint16 = 180

	// CenterAngle is the angle that represents the center position of the servo motors.
	CenterAngle uint16 = 118 // 90, (93 SERVO1), (112 SERVO2)

	// MaxLeftAngle is the maximum left angle for the servo motors.
	MaxLeftAngle uint16 = 30 // (35)

	// MaxRightAngle is the maximum right angle for the servo motors.
	MaxRightAngle uint16 = 30 // (30)

	// IsDirectionInverted indicates if the servo direction is inverted.
	IsDirectionInverted bool = true

	// PWMFrequency is the frequency of the PWM signal used to control the servo motors.
	PWMFrequency uint16 = 330

	// MinPulseWidth is the minimum pulse width in microseconds for the servo motors.
	MinPulseWidth uint32 = 500_000

	// MaxPulseWidth is the maximum pulse width in microseconds for the servo motors.
	MaxPulseWidth uint32 = 2_500_000
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
		ActuationRange,
		CenterAngle,
		MaxLeftAngle,
		MaxRightAngle,
		IsDirectionInverted,
		nil, // internal.Logger,
	)
	if err != tinygoerrors.ErrorCodeNil {
		internal.Logger.ErrorMessageWithErrorCode(
			failedToInitializeServoMessage,
			err,
			true,
		)
		os.Exit(1)
	}
	ServoHandler = servoHandler
}
