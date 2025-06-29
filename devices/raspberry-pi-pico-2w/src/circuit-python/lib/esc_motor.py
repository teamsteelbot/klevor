from asyncio import sleep

from adafruit_motor.servo import ContinuousServo
from pwmio import PWMOut

from .message import OutgoingMessage
from .enums import IncomingCategory, OutgoingCategory
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
    PWM_FREQUENCY = 50
    MIN_PULSE = 1000
    MAX_PULSE = 2000

    # Speed factor to normalize that if positive the motor move forward, and if negative it moves backward
    SPEED_FACTOR = -1.0

    # Speed range
    SPEED_RANGE = (-1.0, 1.0)

    # Common speed values
    SPEED_FAST = 1.0
    SPEED_NORMAL = 0.5
    SPEED_SLOW = 0.25

    # Delay for motor operations
    DELAY = 0.2

    def __init__(
        self, motor_pin: int, frequency: int = PWM_FREQUENCY,
        min_pulse: int = MIN_PULSE, max_pulse: int = MAX_PULSE,
        movement: bool = True, debug: bool = False,
        serial_communication: SerialCommunication = None
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
            max_pulse=max_pulse
        )

        # Set the movement flag and debug mode
        self.__movement = movement
        self.__debug = debug

        # Set the serial communication instance
        self.__serial_communication = serial_communication

        # Initialize the speed to 0
        self.__speed = 0.0
        self.stop()

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
                f"Speed must be between 0 and {cls.SPEED_RANGE[1]}"
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
                f"Speed must be between {cls.SPEED_RANGE[0]} and {cls.SPEED_RANGE[1]}"
            )

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
            # Send the received message
        if self.__debug and self.__serial_communication:
            self.__serial_communication.send_message(
                OutgoingMessage(
                    OutgoingCategory.DEBUG,
                    f"{IncomingCategory.MOTOR_SPEED}={self.__speed}"
                )
            )

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
