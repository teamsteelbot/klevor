package escmotor

import (
	"os"
	"time"

	"machine"

	"github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal"
	internalmovement "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/movement"
	tinygoerrors "github.com/ralvarezdev/tinygo-errors"
	tinygoescmotor "github.com/ralvarezdev/tinygo-escmotor"
)

const (
	// IsPolarityInverted indicates whether the ESC motor's polarity is inverted
	IsPolarityInverted = true

	// PWMFrequency is the frequency for the PWM signal in Hertz
	PWMFrequency = 50

	// MinPulseWidth is the minimum pulse width in microseconds
	MinPulseWidth uint16 = 1000

	// NeutralPulseWidth is the neutral pulse width in microseconds
	NeutralPulseWidth uint16 = 1500

	// MaxPulseWidth is the maximum pulse width in microseconds
	MaxPulseWidth uint16 = 2000

	// MaxSpeed is the maximum speed to run the ESC motor
	MaxSpeed uint16 = 100

	// BackwardToForwardDelay is the delay when changing from backward to forward to be in neutral first
	BackwardToForwardDelay = 500 * time.Millisecond // 1000 ms

	// ForwardToBackwardDelay is the delay when changing from forward to backward to be in neutral first
	ForwardToBackwardDelay = 500 * time.Millisecond // 1000 ms

	// ChangeSteps is the interval to change the speed of the ESC motor
	ChangeSteps = 20
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
		NeutralPulseWidth,
		MaxPulseWidth,
		ChangeSteps,
		IsPolarityInverted,
		MaxSpeed,
		BackwardToForwardDelay,
		ForwardToBackwardDelay,
		nil,
		// internal.Logger,
	)
	if err != tinygoerrors.ErrorCodeNil {
		internal.Logger.ErrorMessageWithErrorCode(
			failedToInitializeEscMotorMessage,
			err,
			true,
		)
		os.Exit(1)
	}
	ESCMotorHandler = escMotorHandler
}
