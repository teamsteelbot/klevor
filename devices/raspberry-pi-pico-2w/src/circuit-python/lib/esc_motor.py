from board import GP2
from pwmio import PWMOut
from adafruit_motor.servo import ContinuousServo
from asyncio import sleep

from .message import OutgoingCategory, OutgoingMessage
from .serial_communication import SerialCommunication

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
    MOTOR_PIN = GP2
    PWM_FREQUENCY = 50
    MIN_PULSE = 1000
    MAX_PULSE = 2000

    # Speed factor to normalize that if positive the motor move forward, and if negative it moves backward
    SPEED_FACTOR = -1.0

    # Common speed values
    SPEED_FAST = 1.0
    SPEED_NORMAL = 0.5
    SPEED_TURN = 0.25

    # Delay for motor operations
    DELAY = 0.15

    def __init__(self, motor_pin: int = MOTOR_PIN, frequency: int = PWM_FREQUENCY,
                 min_pulse: int = MIN_PULSE, max_pulse: int = MAX_PULSE,
                 serial_communication: SerialCommunication = None, movement: bool = True):
        """
        Initializes the ESC motor handler with the specified parameters.

        Args:
            motor_pin (int): The GPIO pin connected to the ESC motor.
            frequency (int): The PWM frequency for the ESC motor.
            min_pulse (int): Minimum pulse width for the ESC motor.
            max_pulse (int): Maximum pulse width for the ESC motor.
            serial_communication (SerialCommunication | None): Optional serial communication handler.
            movement (bool): If True, the motor will be controlled for movement; if False, it will not.
        """
        # Setup PWM output for the ESC motor
        self.__esc_pwm = PWMOut(motor_pin, duty_cycle=0, frequency=frequency)
        self.__esc_motor = ContinuousServo(self.__esc_pwm, min_pulse=min_pulse, max_pulse=max_pulse)

        # If a serial communication handler is provided, use it
        self.__serial_communication = serial_communication

        # Set the movement flag
        self.__movement = movement

        # Initialize the speed to 0
        self.__speed = 0.0
        self.stop()

    @staticmethod
    def _check_speed_half_range(speed: float):
        """
        Check the speed value to ensure it is within the valid half range for ESC motors.
        """
        if not 0 < speed <= 1.0:
            raise ESCMotorError("Speed must be between 0 and 1.0")

    @staticmethod
    def _check_speed_full_range(speed: float):
        """
        Check the speed value to ensure it is within the valid full range for ESC motors.
        """
        if not -1.0 <= speed <= 1.0:
            raise ESCMotorError("Speed must be between -1.0 and 1.0")

    @property
    def speed(self) -> float:
        """
        Returns the current speed of the ESC motor.

        Returns:
            float: Current speed value between -1.0 (full reverse) and 1.0 (full forward).
        """
        return self.__speed

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

        # If a serial communication handler is provided, send the speed message
        if self.__serial_communication:
            self.__serial_communication.send_motor_speed_message(self.__speed)

        # Add a delay to allow the motor to respond
        await sleep(self.DELAY)

    async def stop(self):
        """
        Sets the speed of the ESC motor to 0.
        """
        await self.set_speed(0.0)

    async def forward(self, speed: float):
        """
        Sets the speed of the ESC motor forward.

        Args:
            speed (float): Speed value between 0 and 1.0 (full forward).
        """
        self._check_speed_half_range(speed)
        await self.set_speed(speed)

    async def backward(self, speed: float):
        """
        Sets the speed of the ESC motor backward.

        Args:
            speed (float): Speed value between 0 and 1.0 (full backward).
        """
        self._check_speed_half_range(speed)
        await self.set_speed(-speed)
