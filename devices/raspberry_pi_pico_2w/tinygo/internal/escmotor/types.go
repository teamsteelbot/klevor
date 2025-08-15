package escmotor

import (
	tinygoservo "tinygo.org/x/drivers/servo"

	"math"

	"machine"
	internalenums "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/enums"
)

type (
	// DefaultESCMotor is the default implementation to handle ESC (Electronic Speed Controller) motor operations.
	DefaultESCMotor struct {
		pwm machine.PWM
		pin machine.Pin
		isPolarityInverted bool
		minPulse uint
		maxPulse uint
		servo tinygoservo.Servo
	}

	// Options are the different optional parameters for the DefaultESCMotor constructor
	Options struct {
		IsPolarityInverted bool
		MinPulse uint
		MaxPulse uint
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
func NewOptions(isPolarityInverted bool, minPulse uint, maxPulse uint) *Options {
	return &Options{
		IsPolarityInverted: isPolarityInverted,
		MinPulse: minPulse,
		MaxPulse: maxPulse,
	}
}

// NewDefaultESCMotor creates a new instance of DefaultESCMotor
//
// Parameters:
//
// pwm: The PWM interface to control the ESC motor
// pin: The pin connected to the ESC motor
// options: Optional parameters for the ESC motor configuration
//
// Returns:
//
// An instance of DefaultESCMotor and an error if any occurred during initialization
func NewDefaultESCMotor(pwm machine.PWM, pin machine.Pin, options *Options) (*DefaultESCMotor, error) {
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

	return &DefaultESCMotor{
		pwm,
		pin,
		options.IsPolarityInverted,
		options.MinPulse,
		options.MaxPulse,
		servo,
	}, nil
}

# Speed range
SPEED_RANGE = (-1.0, 1.0)

def __init__(
self, motor_pin: int, frequency: int = PWM_FREQUENCY,
min_pulse: int = MIN_PULSE, max_pulse: int = MAX_PULSE,
movement: bool = True, debug: bool = False,
serial_communication: SerialCommunication = None,
):
"""
Initializes the ESC motor handler with the specified parameters.

Args:
motor_pin (int): The GPIO pin connected to the ESC motor.
frequency (int): The PWM frequency for the ESC motor.
min_pulse (int): Minimum pulse width for the ESC motor.
max_pulse (int): Maximum pulse width for the ESC motor.
movement (bool): If True, the motor will be controlled for movement; if False, it will not.
debug (bool): If True, debug messages will be sent.
serial_communication (SerialCommunication): An instance of SerialCommunication for sending debug messages.
"""
# Setup PWM output for the ESC motor
self.__esc_pwm = PWMOut(motor_pin, duty_cycle=0, frequency=frequency)
self.__esc_motor = ContinuousServo(
self.__esc_pwm,
min_pulse=min_pulse,
max_pulse=max_pulse,
)

# Set the movement flag and debug mode
self.__movement = movement
self.__debug = debug

# Set the serial communication instance
self.__serial_communication = serial_communication

# Initialize the speed to 0
self.__speed = None
self.__esc_motor.throttle = 0
time.sleep(self.DELAY)

@classmethod
def _check_speed_half_range(cls, speed: float):
"""
Check the speed value to ensure it is within the valid half range for ESC motors.

Args:
speed (float): The speed value to check.

Raises:
ESCMotorError: If the speed is not within the valid half range.
"""
if not (0 < speed <= cls.SPEED_RANGE[1]):
raise ESCMotorError(
f"Speed must be between 0 and {cls.SPEED_RANGE[1]}",
)

@classmethod
def _check_speed_full_range(cls, speed: float):
"""
Check the speed value to ensure it is within the valid full range for ESC motors.

Args:
speed (float): The speed value to check.

Raises:
ESCMotorError: If the speed is not within the valid full range.
"""
if not (cls.SPEED_RANGE[0] <= speed <= cls.SPEED_RANGE[1]):
raise ESCMotorError(
f"Speed must be between {cls.SPEED_RANGE[0]} and {cls.SPEED_RANGE[1]}",
)

async def set_speed(self, speed: float):
"""
Sets the speed of the ESC motor.

Args:
speed (float): Speed value between -1.0 (full reverse) and 1.0 (full forward).
"""
# Check if the speed is the same as the current speed
if self.__speed == speed * self.SPEED_FACTOR:
return

# Check if the speed is within the full range
self._check_speed_full_range(speed)
self.__speed = speed * self.SPEED_FACTOR
if self.__movement:
self.__esc_motor.throttle = self.__speed

# Send the received message
if self.__debug and self.__serial_communication:
self.__serial_communication.send_message(
OutgoingMessage(
OutgoingCategory.DEBUG,
f"{IncomingCategory.MOTOR_SPEED}={self.__speed}",
),
)

# Add a delay to allow the motor to respond
await sleep(self.DELAY)

// Stop sets the ESC motor speed to 0 (stop).
func (e *DefaultESCMotor) Stop() {
	e.SetSpeed(0)
}

// GoForward sets the ESC motor speed forward.
//
// Parameters:
//
// speed: Speed value between 0 (stop) and half of the maximum pulse (full forward).
func (e *DefaultESCMotor) GoForward(speed uint) {
	e.SetSpeed(speed)
}

// GoBackward sets the ESC motor speed backward.
//
// Parameters:
//
// speed: Speed value between 0 (stop) and half of the maximum pulse (full backward).
func (e *DefaultESCMotor) GoBackward(speed uint) {
	e.SetSpeed(-speed)
}