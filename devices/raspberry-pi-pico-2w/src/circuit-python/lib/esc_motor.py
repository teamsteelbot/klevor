from board import GP2
from pwmio import PWMOut
from adafruit_motor.servo import ContinuousServo

class ESCMotorError(Exception):
    """
    Custom exception class for ESC motor errors.
    """
    def __init__(self, message):
        """
        Initializes the ESCMotorError with a custom message.
        """
        super().__init__(message)
        self.message = message

    def __str__(self):
        """
        Returns a string representation of the ESCMotorError.
        """
        return f"ESC Motor Error: {self.message}"


class ESCMotorHandler:
    """
    A class to handle ESC (Electronic Speed Controller) motor operations.
    """
    # Default configuration
    ESC_MOTOR_PIN = GP2
    ESC_PWM_FREQUENCY = 50
    ESC_MIN_PULSE = 1000
    ESC_MAX_PULSE = 2000

    def __init__(self, motor_pin: int = ESC_MOTOR_PIN, frequency: int = ESC_PWM_FREQUENCY,
                    min_pulse: int = ESC_MIN_PULSE, max_pulse: int = ESC_MAX_PULSE):
        """
        Initializes the ESC motor handler with the specified parameters.
        """
        # Setup PWM output for the ESC motor
        self.__esc_pwm = PWMOut(motor_pin, duty_cycle=0, frequency=frequency)
        self.__esc_motor = ContinuousServo(self.__esc_pwm, min_pulse=min_pulse, max_pulse=max_pulse)

        # Set the motor to neutral position
        self.__speed = 0.0
        self.__esc_motor.throttle = self.__speed

    @property
    def speed(self) -> float:
        """
        Returns the current speed of the ESC motor.
        """
        return self.__speed

    @speed.setter
    def speed(self, speed: float):
        """
        Sets the speed of the ESC motor.

        Args:
            speed (float): Speed value between -1.0 (full reverse) and 1.0 (full forward).
        """
        if not -1.0 <= speed <= 1.0:
            raise ESCMotorError("Speed must be between -1.0 and 1.0")

        # Set the throttle of the ESC motor
        self.__speed = speed
        self.__esc_motor.throttle = speed