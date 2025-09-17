package escmotor

import (
	"os"
	"time"

	"machine"

	"github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal"
	internalmovement "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/movement"
	tinygoescmotor "github.com/ralvarezdev/tinygo-escmotor"
	tinygoerrors "github.com/ralvarezdev/tinygo-errors"
)

const (
	// IsPolarityInverted indicates whether the ESC motor's polarity is inverted
	IsPolarityInverted = false

	// PWMFrequency is the frequency for the PWM signal in Hertz
	PWMFrequency = 50

	// MinPulseWidth is the minimum pulse width in microseconds
	MinPulseWidth uint16 = 1000

	// MaxPulseWidth is the maximum pulse width in microseconds
	MaxPulseWidth uint16 = 2000

	// MaxSpeed is the maximum speed to run the ESC motor
	MaxSpeed uint16 = 100

	// ChangeInterval is the interval to change the speed of the ESC motor
	ChangeInterval = 5

	// ChangeInternalDelay is the internal delay to change the speed of the ESC motor
	ChangeInternalDelay = 8 * time.Millisecond
)

var (
	// ESCMotorHandler is the default handler for ESC motors
	ESCMotorHandler tinygoescmotor.Handler

	// failedToInitializeEscMotorMessage is the message printed when esc motor initialization fails
	failedToInitializeEscMotorMessage = []byte("Failed to initialize ESC Motor handler:")
)

func init() {
	escMotorHandler, err := tinygoescmotor.NewDefaultHandler(
		machine.PWM0,
		machine.GPIO1,
		nil,
		internalmovement.Handler.IsEnabled,
		PWMFrequency,
		MinPulseWidth,
		MaxPulseWidth,
		ChangeInterval,
		ChangeInternalDelay,
		IsPolarityInverted,
		MaxSpeed,
		nil, // internal.Logger
	)
	if err != tinygoerrors.ErrorCodeNil {
		internal.Logger.ErrorMessageWithErrorCode(failedToInitializeEscMotorMessage, err, true)
		os.Exit(1)
	}
	ESCMotorHandler = escMotorHandler
}