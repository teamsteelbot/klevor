package escmotor

import (
	"time"

	"machine"

	"github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal"
	internaldebug "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/debug"
	internalmovement "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/movement"
	internalpullupenabler "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/pullup/enabler"
	internalusbcdc "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/usbcdc"
	tinygoservo "tinygo.org/x/drivers/servo"
	tinygotypes "github.com/ralvarezdev/tinygo-types"
)

type (
	// DefaultHandler is the default implementation to handle ESC (Electronic Speed Controller) motor operations.
	DefaultHandler struct {
		usbCDCHandler      internalusbcdc.Handler
		debugHandler       internalpullupenabler.Handler
		movementHandler    internalpullupenabler.Handler
		isPolarityInverted bool
		frequency          uint16
		minPulseWidth      uint16
		halfPulseWidth     uint16
		maxPulseWidth      uint16
		rangePulseWidth    uint16
		servo              tinygoservo.Servo
		speed              int16
		microseconds       uint16
	}

	// Options are the different optional parameters for the DefaultHandler constructor
	Options struct {
		IsPolarityInverted bool
		Frequency          uint16
		MinPulseWidth      uint16
		MaxPulseWidth      uint16
	}
)

// NewOptions creates a new instance of Options
//
// Parameters:
//
// isPolarityInverted: Whether the motor polarity is inverted
// frequency: Frequency for the PWM signal
// minPulseWidth: Minimum pulse width for the ESC motor
// maxPulseWidth: Maximum pulse width for the ESC motor
//
// Returns:
//
// An instance of Options
func NewOptions(
	isPolarityInverted bool,
	frequency uint16,
	minPulseWidth uint16,
	maxPulseWidth uint16,
) *Options {
	return &Options{
		isPolarityInverted,
		frequency,
		minPulseWidth,
		maxPulseWidth,
	}
}

// NewDefaultHandler creates a new instance of DefaultHandler
//
// Parameters:
//
// pwm: The PWM interface to control the ESC motor
// pin: The pin connected to the ESC motor
// usbCDCHandler: The USB CDC handler to send messages
// debugHandler: The debug pull-up handler to check if the debug mode is enabled
// movementHandler: The movement pull-up handler to check if the movement is enabled
// options: Optional parameters for the ESC motor configuration
//
// Returns:
//
// An instance of DefaultHandler and an error if any occurred during initialization
func NewDefaultHandler(
	pwm tinygoservo.PWM,
	pin machine.Pin,
	usbCDCHandler internalusbcdc.Handler,
	debugHandler, movementHandler internalpullupenabler.Handler,
	options *Options,
) (*DefaultHandler, tinygotypes.ErrorCode) {
	// Check if the USB CDC handler is nil
	if usbCDCHandler == nil {
		return nil, internalusbcdc.ErrorCodeUSBCDCNilHandler
	}

	// Check if the debug pull-up handler is nil
	if debugHandler == nil {
		return nil, internaldebug.ErrorCodeDebugNilHandler
	}

	// Check if the movement pull-up handler is nil
	if movementHandler == nil {
		return nil, internalmovement.ErrorCodeMovementNilHandler
	}

	// Check if options are nil
	if options == nil {
		return nil, ErrorCodeESCMotorNilOptions
	}

	// Configure the PWM
	if err := pwm.Configure(
		machine.PWMConfig{
			Period: uint64(time.Second / time.Duration(options.Frequency)),
		},
	); err != nil {
		return nil, internal.ErrorCodeFailedToConfigurePWM
	}

	// Create a new instance of the servo
	servo, err := tinygoservo.New(pwm, pin)
	if err != nil {
		return nil, ErrorCodeESCMotorFailedToInitializeServo
	}

	// Calculate the half pulse and range pulse
	halfPulseWidth := (options.MaxPulseWidth + options.MinPulseWidth) / 2
	rangePulseWidth := options.MaxPulseWidth - options.MinPulseWidth

	// Initialize the ESC motor with the provided parameters
	handler := &DefaultHandler{
		usbCDCHandler,
		debugHandler,
		movementHandler,
		options.IsPolarityInverted,
		options.Frequency,
		options.MinPulseWidth,
		halfPulseWidth,
		options.MaxPulseWidth,
		rangePulseWidth,
		servo,
		int16(StopSpeed), // Initial speed is set to 0
		StopMicroseconds,
	}

	// Stop the motor initially
	_ = handler.Stop()

	return handler, tinygotypes.ErrorCodeNil
}

// SetSpeed sets the ESC motor speed.
//
// Parameters:
//
// speed: Speed value between -half of the maximum pulse (full backward) and half of the maximum pulse (full forward).
func (e *DefaultHandler) SetSpeed(speed uint16, isForward bool) tinygotypes.ErrorCode {
	// Check if the is polarity inverted
	if e.isPolarityInverted {
		isForward = !isForward
	}

	// Check if the speed is within the valid range
	if speed > MaxSpeed {
		return ErrorCodeESCMotorSpeedOutOfRange
	}

	// Calculate the microseconds based on the speed and direction
	var microseconds uint16
	if isForward {
		microseconds = e.halfPulseWidth + speed
		e.speed = int16(speed)
	} else {
		microseconds = e.halfPulseWidth - speed
		e.speed = -int16(speed)
	}

	// Ensure the microseconds is within the valid range
	if microseconds < e.minPulseWidth {
		return ErrorCodeESCMotorSpeedBelowMinPulseWidth
	} else if microseconds > e.maxPulseWidth {
		return ErrorCodeESCMotorSpeedAboveMaxPulseWidth
	}

	// Set the servo microseconds if movement is enabled
	if e.movementHandler.IsEnabled() {
		// Gradually change the speed to avoid sudden jumps
		if e.microseconds > microseconds {
			for us := e.microseconds; us > microseconds; us -= ChangeInterval {
				e.servo.SetMicroseconds(int16(us))
				time.Sleep(ChangeInternalDelay)
			}
		} else if e.microseconds < microseconds {
			for us := e.microseconds; us < microseconds; us += ChangeInterval {
				e.servo.SetMicroseconds(int16(us))
				time.Sleep(ChangeInternalDelay)
			}
		}

		// Finally, set the exact microseconds
		if e.microseconds != microseconds {
			e.servo.SetMicroseconds(int16(microseconds))

			// Update the current microseconds
			e.microseconds = microseconds
		}
	} else {
		microseconds = e.halfPulseWidth
	}

	// Send the debug message if the debug handler is enabled
	if e.debugHandler.IsEnabled() && e.usbCDCHandler != nil {
		if err := e.usbCDCHandler.SendMessage(
			internalusbcdc.NewOutgoingDebugMessage(
				internalusbcdc.DebugReceivedMotorSpeed,
			),
		); err != tinygotypes.ErrorCodeNil {
			return ErrorCodeESCMotorFailedToSendDebugMotorSpeedMessage
		}
	}
	return tinygotypes.ErrorCodeNil
}

// GetSpeed returns the current speed of the ESC motor.
//
// Returns:
//
// The current speed of the ESC motor as an int16 value.
func (e *DefaultHandler) GetSpeed() int16 {
	return e.speed
}

// Stop sets the ESC motor speed to 0 (stop).
//
// Returns:
//
// An error if the speed could not be set to 0, otherwise nil.
func (e *DefaultHandler) Stop() tinygotypes.ErrorCode {
	return e.SetSpeed(StopSpeed, true)
}

// SetSpeedForward sets the ESC motor speed forward.
//
// Parameters:
//
// speed: Speed value between 0 (stop) and half of the maximum pulse (full forward).
//
// Returns:
//
// An error if the speed could not be set, otherwise nil.
func (e *DefaultHandler) SetSpeedForward(speed uint16) tinygotypes.ErrorCode {
	return e.SetSpeed(speed, true)
}

// SetSpeedBackward sets the ESC motor speed backward.
//
// Parameters:
//
// speed: Speed value between 0 (stop) and half of the maximum pulse (full backward).
//
// Returns:
//
// An error if the speed could not be set, otherwise nil.
func (e *DefaultHandler) SetSpeedBackward(speed uint16) tinygotypes.ErrorCode {
	return e.SetSpeed(speed, false)
}

// SetSpeedBasedOnReceivedMessage sets the motor speed based on the received message
//
// Parameters:
//
// message: The incoming message containing the motor speed command
//
// Returns:
//
// An error if the motor speed could not be set, otherwise nil
func (e *DefaultHandler) SetSpeedBasedOnReceivedMessage(message *internalusbcdc.IncomingMessage) tinygotypes.ErrorCode {
	// Check if the message is nil
	if message == nil {
		return internalusbcdc.ErrorCodeUSBCDCNilIncomingMessage
	}

	// Check if the motor speed should be retrieved from the message
	var motorSpeed uint16
	if message.Category != internalusbcdc.IncomingCategoryMotorSpeedStop {
		// Get int16 speed from message content
		speed, err := message.GetContentAsUint16()
		if err != tinygotypes.ErrorCodeNil {
			return ErrorCodeESCMotorInvalidMotorSpeedValue
		}
		motorSpeed = speed
	}

	// Check the motor speed category
	switch message.Category {
	case internalusbcdc.IncomingCategoryMotorSpeedStop:
		return e.Stop()
	case internalusbcdc.IncomingCategoryMotorSpeedForward:
		return e.SetSpeedForward(motorSpeed)
	case internalusbcdc.IncomingCategoryMotorSpeedBackward:
		return e.SetSpeedBackward(motorSpeed)
	default:
		return ErrorCodeESCMotorUnknownMotorSpeedCategory
	}
}
