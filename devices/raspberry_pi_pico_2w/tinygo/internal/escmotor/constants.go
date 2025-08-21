package escmotor

import (
	"fmt"

	"machine"

	internaldebug "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/debug"
	internalmovement "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/movement"
	internalusbcdc "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/usbcdc"
)

const (
	// StopSpeed is the speed to stop the ESC motor
	StopSpeed = 0

	// DefaultIsPolarityInverted indicates whether the ESC motor's polarity is inverted
	DefaultIsPolarityInverted = false

	// DefaultPWMFrequency is the frequency for the PWM signal in Hertz
	DefaultPWMFrequency = 50

	// DefaultMinPulseWidth is the default minimum pulse width in microseconds
	DefaultMinPulseWidth uint16 = 1000

	// DefaultMaxPulseWidth is the default maximum pulse width in microseconds
	DefaultMaxPulseWidth uint16 = 2000
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
	if err != nil {
		panic(fmt.Errorf("failed to initialize esc motor handler: %w", err))
	}
	ESCMotorHandler = escMotorHandler
}
