package escmotor

import (
	"time"

	"machine"

	internaldebug "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/debug"
	internalmovement "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/movement"
	internalusbcdc "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/usbcdc"
	tinygotypes "github.com/ralvarezdev/tinygo-types"
	"github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal"
)

const (
	// DefaultIsPolarityInverted indicates whether the ESC motor's polarity is inverted
	DefaultIsPolarityInverted = false

	// DefaultPWMFrequency is the frequency for the PWM signal in Hertz
	DefaultPWMFrequency = 50

	// DefaultMinPulseWidth is the default minimum pulse width in microseconds
	DefaultMinPulseWidth uint16 = 1000

	// DefaultMaxPulseWidth is the default maximum pulse width in microseconds
	DefaultMaxPulseWidth uint16 = 2000

	// StopSpeed is the speed to stop the ESC motor
	StopSpeed uint16 = 0

	// MaxSpeed is the maximum speed to run the ESC motor
	MaxSpeed uint16 = 500

	// StopMicroseconds is the microseconds to stop the ESC motor
	StopMicroseconds = (DefaultMaxPulseWidth + DefaultMinPulseWidth) / 2

	// ChangeInterval is the interval to change the speed of the ESC motor
	ChangeInterval = 20

	// ChangeInternalDelay is the internal delay to change the speed of the ESC motor
	ChangeInternalDelay = 5 * time.Millisecond
)

var (
	// DefaultOptions is the default options for the ESC motor handler
	DefaultOptions = NewOptions(
		DefaultIsPolarityInverted,
		DefaultPWMFrequency,
		DefaultMinPulseWidth,
		DefaultMaxPulseWidth,
	)

	// ESCMotorHandler is the default handler for ESC motors
	ESCMotorHandler Handler

	// failedToInitializeEscMotorMessage is the message printed when esc motor initialization fails
	failedToInitializeEscMotorMessage = []byte("Failed to initialize ESC Motor handler:")
)

func init() {
	escMotorHandler, err := NewDefaultHandler(
		machine.PWM0,
		machine.GPIO1,
		internalusbcdc.USBCDCHandler,
		internaldebug.Handler,
		internalmovement.Handler,
		DefaultOptions,
	)
	if err != tinygotypes.ErrorCodeNil {
		internal.Logger.ErrorMessageWithErrorCode(failedToInitializeEscMotorMessage, err)
		return
	}
	ESCMotorHandler = escMotorHandler
}
