package servo

import (
	"machine"

	internaldebug "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/debug"
	internalmovement "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/movement"
	internalusbcdc "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/usbcdc"
	tinygotypes "github.com/ralvarezdev/tinygo-types"
	"github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal"
)

const (
	// CenterAngle is the angle that represents the center position of the servo motors.
	CenterAngle uint16 = 90

	// LeftLimitAngle is the angle that represents the left limit position of the servo motors.
	LeftLimitAngle uint16 = 0

	// RightLimitAngle is the angle that represents the right limit position of the servo motors.
	RightLimitAngle uint16 = 180

	// MaxAngle is the maximum angle for the servo motors.
	MaxAngle uint16 = 15

	// DefaultIsDirectionInverted indicates if the servo direction is inverted.
	DefaultIsDirectionInverted bool = true

	// DefaultPWMFrequency is the frequency of the PWM signal used to control the servo motors.
	DefaultPWMFrequency uint16 = 330

	// DefaultMinPulseWidth is the minimum pulse width in microseconds for the servo motors.
	DefaultMinPulseWidth uint16 = 500

	// DefaultMaxPulseWidth is the maximum pulse width in microseconds for the servo motors.
	DefaultMaxPulseWidth uint16 = 2500
)

var (
	// DefaultOptions holds the default options for the servo motors.
	DefaultOptions = NewOptions(
		DefaultIsDirectionInverted,
		DefaultPWMFrequency,
		DefaultMinPulseWidth,
		DefaultMaxPulseWidth,
	)

	// ServoHandler is the default servo handler using the Raspberry Pi Pico 2W's PWM1 and GPIO2.
	ServoHandler Handler

	// failedToInitializeServoMessage is the message printed when servo initialization fails
	failedToInitializeServoMessage = []byte("Failed to initialize Servo handler:")
)

func init() {
	servoHandler, err := NewDefaultHandler(
		machine.PWM2,
		machine.GPIO5,
		internalusbcdc.USBCDCHandler,
		internaldebug.Handler,
		internalmovement.Handler,
		DefaultOptions,
	)
	if err != tinygotypes.ErrorCodeNil {
		internal.Logger.ErrorMessageWithErrorCode(failedToInitializeServoMessage, err)
	}
	ServoHandler = servoHandler
}
