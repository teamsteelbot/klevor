package servo

import (
	"fmt"
	"time"

	"machine"

	internaldebug "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/debug"
	internalmovement "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/movement"
	internalpullupenabler "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/pullup/enabler"
	internalusbcdc "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/usbcdc"
	internalusbcdcenums "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/usbcdc/enums"
	tinygoservo "tinygo.org/x/drivers/servo"
)

type (
	// DefaultHandler is the default implementation of the Servo interface
	DefaultHandler struct {
		usbCDCHandler       internalusbcdc.Handler
		debugHandler        internalpullupenabler.Handler
		movementHandler     internalpullupenabler.Handler
		isDirectionInverted bool
		frequency           uint16
		minPulseWidth       uint16
		halfPulseWidth      uint16
		maxPulseWidth       uint16
		rangePulseWidth     uint16
		servo               tinygoservo.Servo
		angle               uint16
	}

	// Options defines the options for the servo motor
	Options struct {
		IsDirectionInverted bool
		Frequency           uint16
		MinPulseWidth       uint16
		MaxPulseWidth       uint16
	}
)

// NewOptions creates a new Options instance
//
// Parameters:
//
// isDirectionInverted: Whether the direction of the servo motor is inverted
// frequency: The frequency of the PWM signal
// minPulseWidth: The minimum pulse width for the servo motor
// maxPulseWidth: The maximum pulse width for the servo motor
//
// Returns:
//
// An instance of Options
func NewOptions(
	isDirectionInverted bool,
	frequency uint16,
	minPulseWidth uint16,
	maxPulseWidth uint16,
) *Options {
	return &Options{
		isDirectionInverted,
		frequency,
		minPulseWidth,
		maxPulseWidth,
	}
}

// NewDefaultHandler creates a new instance of DefaultHandler
//
// Parameters:
//
// pwm: The PWM interface to control the servo
// pin: The pin connected to the servo
// usbCDCHandler: The USB CDC handler to send messages
// debugHandler: The debug pull-down handler to check if the debug mode is enabled
// movementHandler: The movement pull-down handler to check if the movement is enabled
// options: Optional parameters for the servo configuration
//
// Returns:
//
// An instance of DefaultHandler and an error if any occurred during initialization
func NewDefaultHandler(
	pwm tinygoservo.PWM,
	pin machine.Pin,
	usbCDCHandler internalusbcdc.Handler,
	debugHandler,
	movementHandler internalpullupenabler.Handler,
	options *Options,
) (*DefaultHandler, error) {
	// Check if the USB CDC handler is nil
	if usbCDCHandler == nil {
		return nil, internalusbcdc.ErrNilHandler
	}

	// Check if the debug pull-down handler is nil
	if debugHandler == nil {
		return nil, internaldebug.ErrNilHandler
	}

	// Check if the movement pull-down handler is nil
	if movementHandler == nil {
		return nil, internalmovement.ErrNilHandler
	}

	// Check if the options are nil
	if options == nil {
		return nil, ErrNilOptions
	}

	// Configure the PWM
	if err := pwm.Configure(
		machine.PWMConfig{
			Period: uint64(time.Second / time.Duration(options.Frequency)),
		},
	); err != nil {
		return nil, err
	}

	// Create a new instance of the servo
	servo, err := tinygoservo.New(pwm, pin)
	if err != nil {
		return nil, err
	}

	// Calculate the half pulse and range pulse
	halfPulseWidth := (options.MaxPulseWidth + options.MinPulseWidth) / 2
	rangePulseWidth := options.MaxPulseWidth - options.MinPulseWidth

	// Initialize the servo with the provided parameters
	handler := &DefaultHandler{
		usbCDCHandler,
		debugHandler,
		movementHandler,
		options.IsDirectionInverted,
		options.Frequency,
		options.MinPulseWidth,
		halfPulseWidth,
		options.MaxPulseWidth,
		rangePulseWidth,
		servo,
		CenterAngle, // Default angle set to 90 degrees
	}

	// Center the servo on initialization
	_ = handler.Center()

	return handler, nil
}

// GetAngle returns the current angle of the servo motor
//
// Returns:
//
// The current angle of the servo motor
func (s *DefaultHandler) GetAngle() uint16 {
	return s.angle
}

// SetAngle sets the angle of the servo motor
//
// Parameters:
//
// angle: The angle to set the servo motor to, must be between 0 and the actuation range
func (s *DefaultHandler) SetAngle(angle uint16) error {
	// Check if the angle is within the valid range
	if angle < LeftLimitAngle || angle > RightLimitAngle {
		return fmt.Errorf(
			ErrInvalidAngle,
			LeftLimitAngle,
			RightLimitAngle,
			angle,
		)
	}

	// Check if the angle is the same as the current angle
	if angle == s.angle {
		return nil
	}

	// Check if the direction is inverted
	if s.isDirectionInverted {
		angle = RightLimitAngle - (angle - LeftLimitAngle)
	}

	// Update the current angle
	s.angle = angle

	// Set the servo angle
	if s.movementHandler.IsEnabled() {
		if err := s.servo.SetAngleWithMicroseconds(
			int(angle),
			int(s.minPulseWidth),
			int(s.maxPulseWidth),
		); err != nil {
			return err
		}
	}

	// Send a debug message if debug mode is enabled
	if s.debugHandler.IsShorted() && s.usbCDCHandler != nil {
		err := s.usbCDCHandler.SendMessage(
			internalusbcdc.NewOutgoingMessageFromUint8Content(
				internalusbcdcenums.OutgoingCategoryDebug,
				uint8(internalusbcdcenums.DebugReceivedServoAngle),
			),
		)
		if err != nil {
			return fmt.Errorf(ErrSendingDebugServoAngleMessage, err)
		}
	}

	return nil
}

// IsAngleCentered checks if the servo motor angle is centered
//
// Returns:
//
// True if the servo motor is centered, false otherwise
func (s *DefaultHandler) IsAngleCentered() bool {
	return s.angle == CenterAngle
}

// SetAngleToCenter centers the servo motor to the middle position
//
// Returns:
//
// An error if the servo motor could not be centered
func (s *DefaultHandler) SetAngleToCenter() error {
	return s.SetAngle(CenterAngle)
}

// SetAngleRelativeToCenter sets the angle of the servo motor relative to the center position
//
// Parameters:
//
// relativeAngle: The relative angle value between -90 and 90 degrees
//
// Returns:
//
// An error if the relative angle is not within the left and right limits
func (s *DefaultHandler) SetAngleRelativeToCenter(relativeAngle int16) error {
	// Calculate the absolute angle based on the center angle and relative angle
	absoluteAngle := int16(CenterAngle) + relativeAngle

	// Check if the absolute angle is within the left and right limits
	if absoluteAngle < int16(LeftLimitAngle) || absoluteAngle > int16(RightLimitAngle) {
		return fmt.Errorf(
			ErrInvalidAngle,
			LeftLimitAngle,
			RightLimitAngle,
			absoluteAngle,
		)
	}

	// Set the servo angle
	return s.SetAngle(uint16(absoluteAngle))
}

// SetAngleToRight sets the servo motor to the right by a specified angle
//
// Parameters:
//
// angle: The angle value to move the servo to the right, must be between 0 and the right limit
//
// Returns:
//
// An error if the angle is not within the right limit
func (s *DefaultHandler) SetAngleToRight(angle uint16) error {
	return s.SetAngleRelativeToCenter(int16(angle))
}

// SetAngleToLeft sets the servo motor to the left by a specified angle
//
// Parameters:
//
// angle: The angle value to move the servo to the left, must be between 0 and the left limit
//
// Returns:
//
// An error if the angle is not within the left limit
func (s *DefaultHandler) SetAngleToLeft(angle uint16) error {
	return s.SetAngleRelativeToCenter(-int16(angle))
}
