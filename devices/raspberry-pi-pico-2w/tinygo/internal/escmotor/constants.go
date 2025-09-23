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
	IsPolarityInverted = false

	// PWMFrequency is the frequency for the PWM signal in Hertz
	PWMFrequency = 50

	// MinPulseWidth is the minimum pulse width
	MinPulseWidth uint32 = 1_000_000

	// NeutralPulseWidth is the neutral pulse width
	NeutralPulseWidth uint32 = 1_500_000

	// MaxPulseWidth is the maximum pulse width
	MaxPulseWidth uint32 = 2_000_000

	// MaxForwardSpeed is the maximum speed to run the ESC motor
	MaxForwardSpeed = 0.175 // 0.175, 0.2

	// MaxBackwardSpeed is the maximum speed to run the ESC motor in backward direction
	MaxBackwardSpeed = 0.225

	// BackwardToForwardDelay is the delay when changing from backward to forward to be in neutral first
	BackwardToForwardDelay = 1000 * time.Millisecond // (1000 ms), 500ms, 250ms, 150ms (for really short times)

	// ForwardToBackwardDelay is the delay when changing from forward to backward to be in neutral first
	ForwardToBackwardDelay = 1000 * time.Millisecond // (1000 ms), 500ms, 250ms (for really short times)
)

var (
	// PulseSteps is the interval of pulse steps when changing speed
	PulseSteps uint32 = 20_000 // (20_000), 10_000

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
		IsPolarityInverted,
		MaxForwardSpeed,
		MaxBackwardSpeed,
		nil, // &PulseSteps,
		BackwardToForwardDelay,
		ForwardToBackwardDelay,
		internal.Logger,
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
