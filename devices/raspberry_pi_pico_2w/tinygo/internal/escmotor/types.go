package escmotor

import (
	"fmt"
	"machine"

	"github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/debug"
	"github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/movement"
	pulldownenabler "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/pulldown/enabler"
	"github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/usbcdc"
	usbcdcenums "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/usbcdc/enums"
	tinygoservo "tinygo.org/x/drivers/servo"
)

type (
	// DefaultESCMotor is the default implementation to handle ESC (Electronic Speed Controller) motor operations.
	DefaultESCMotor struct {
		usbCDCHandler      usbcdc.Handler
		debugHandler       pulldownenabler.Handler
		movementHandler    pulldownenabler.Handler
		pwm                machine.PWM
		pin                machine.Pin
		isPolarityInverted bool
		minPulse           uint16
		halfPulse          uint16
		maxPulse           uint16
		rangePulse         uint16
		servo              tinygoservo.Servo
	}

	// Options are the different optional parameters for the DefaultESCMotor constructor
	Options struct {
		IsPolarityInverted bool
		MinPulse           uint16
		MaxPulse           uint16
	}
)

// NewOptions creates a new instance of Options
//
// Parameters:
//
// isPolarityInverted: Whether the motor polarity is inverted
// minPulse: Minimum pulse width for the ESC motor
// maxPulse: Maximum pulse width for the ESC motor
//
// Returns:
//
// An instance of Options
func NewOptions(
	isPolarityInverted bool,
	minPulse uint16,
	maxPulse uint16,
) *Options {
	return &Options{
		IsPolarityInverted: isPolarityInverted,
		MinPulse:           minPulse,
		MaxPulse:           maxPulse,
	}
}

// NewDefaultESCMotor creates a new instance of DefaultESCMotor
//
// Parameters:
//
// pwm: The PWM interface to control the ESC motor
// pin: The pin connected to the ESC motor
// usbCDCHandler: The USB CDC handler to send messages
// debugHandler: The debug pull-down handler to check if the debug mode is enabled
// movementHandler: The movement pull-down handler to check if the movement is enabled
// options: Optional parameters for the ESC motor configuration
//
// Returns:
//
// An instance of DefaultESCMotor and an error if any occurred during initialization
func NewDefaultESCMotor(
	pwm machine.PWM,
	pin machine.Pin,
	usbCDCHandler usbcdc.Handler,
	debugHandler, movementHandler pulldownenabler.Handler,
	options *Options,
) (*DefaultESCMotor, error) {
	// Check if the USB CDC handler is nil
	if usbCDCHandler == nil {
		return nil, usbcdc.ErrNilHandler
	}

	// Check if the debug pull-down handler is nil
	if debugHandler == nil {
		return nil, debug.ErrNilHandler
	}

	// Check if the movement pull-down handler is nil
	if movementHandler == nil {
		return nil, movement.ErrNilHandler
	}

	// Create a new instance of the servo
	servo, err := tinygoservo.New(pwm, pin)
	if err != nil {
		return nil, err
	}

	// Check if options is nil
	if options == nil {
		options = &Options{
			IsPolarityInverted: DefaultIsPolarityInverted,
			MinPulse:           DefaultMinPulse,
			MaxPulse:           DefaultMaxPulse,
		}
	}

	// Calculate the half pulse and range pulse
	halfPulse := (options.MaxPulse + options.MinPulse) / 2
	rangePulse := options.MaxPulse - options.MinPulse

	// Initialize the ESC motor with the provided parameters
	escMotor := &DefaultESCMotor{
		usbCDCHandler,
		debugHandler,
		movementHandler,
		pwm,
		pin,
		options.IsPolarityInverted,
		options.MinPulse,
		halfPulse,
		options.MaxPulse,
		rangePulse,
		servo,
	}

	// Stop the motor initially
	_ = escMotor.Stop()

	return escMotor, nil
}

// SetSpeed sets the ESC motor speed.
//
// Parameters:
//
// speed: Speed value between -half of the maximum pulse (full backward) and half of the maximum pulse (full forward).
func (e *DefaultESCMotor) SetSpeed(speed uint16, isForward bool) error {
	// Check if the is polarity inverted
	if e.isPolarityInverted {
		isForward = !isForward
	}

	// Calculate the microseconds based on the speed and direction
	var microseconds uint16
	if isForward {
		microseconds = e.halfPulse + speed
	} else {
		microseconds = e.halfPulse - speed
	}

	// Ensure the microseconds is within the valid range
	if microseconds < e.minPulse {
		return fmt.Errorf(
			ErrSpeedBelowMinPulseWidth,
			e.minPulse,
			-e.rangePulse/2,
		)
	} else if microseconds > e.maxPulse {
		return fmt.Errorf(
			ErrSpeedAboveMaxPulseWidth,
			e.maxPulse,
			e.rangePulse/2,
		)
	}

	// Set the servo microseconds if movement is enabled
	if e.movementHandler.IsEnabled() {
		e.servo.SetMicroseconds(int16(microseconds))
	} else {
		microseconds = e.halfPulse
	}

	// Send the debug message if the debug handler is enabled
	if e.debugHandler.IsEnabled() {
		err := e.usbCDCHandler.SendMessage(
			usbcdc.NewOutgoingMessageFromUint8Content(
				usbcdcenums.OutgoingCategoryDebug,
				uint8(usbcdcenums.DebugReceivedMotorSpeed),
			),
		)
		if err != nil {
			return fmt.Errorf(ErrSendingDebugMotorSpeedMessage, err)
		}
	}
	return nil
}

// Stop sets the ESC motor speed to 0 (stop).
//
// Returns:
//
// An error if the speed could not be set to 0, otherwise nil.
func (e *DefaultESCMotor) Stop() error {
	return e.SetSpeed(0, true)
}

// GoForward sets the ESC motor speed forward.
//
// Parameters:
//
// speed: Speed value between 0 (stop) and half of the maximum pulse (full forward).
//
// Returns:
//
// An error if the speed could not be set, otherwise nil.
func (e *DefaultESCMotor) GoForward(speed uint16) error {
	return e.SetSpeed(speed, true)
}

// GoBackward sets the ESC motor speed backward.
//
// Parameters:
//
// speed: Speed value between 0 (stop) and half of the maximum pulse (full backward).
//
// Returns:
//
// An error if the speed could not be set, otherwise nil.
func (e *DefaultESCMotor) GoBackward(speed uint16) error {
	return e.SetSpeed(speed, false)
}
