import board
from pwmio import PWMOut
from adafruit_motor.servo import Servo
from asyncio import sleep

from .message import Message, Category
from .serial_communication import SerialCommunication

class ServoError(Exception):
    """
    Custom exception class for servo motor errors.
    """
    def __init__(self, message):
        """
        Initializes the ServoError with a custom message.
        """
        super().__init__(message)
        self.message = message

    def __str__(self):
        """
        Returns a string representation of the ServoError.
        """
        return f"Servo Error: {self.message}"

class ServoHandler:
    """
    A class to handle servo motor operations.
    """
    # Default configuration
    SERVO_PIN = board.GP13
    PWM_FREQUENCY = 50
    MIN_PULSE = 500
    MAX_PULSE = 2500
    ACTUATION_RANGE = 180
    CENTER_ANGLE = 90

    # Angle factor to normalize that when subtracting the servo moves to the left, and adding moves to the right
    ANGLE_FACTOR = -1

    # Common angle values
    BIG_TURN_ANGLE = 35
    MEDIUM_TURN_ANGLE = 25
    SMALL_TURN_ANGLE = 15

    # Delay
    DELAY = 0.05

    def __init__(self, servo_pin: int = SERVO_PIN, frequency: int = PWM_FREQUENCY,
                    min_pulse: int = MIN_PULSE, max_pulse: int = MAX_PULSE,
                    actuation_range: int = ACTUATION_RANGE, serial_communication: SerialCommunication = None):
        """
        Initializes the servo handler with the specified parameters.

        Args:
            servo_pin (int): The GPIO pin for the servo motor.
            frequency (int): The PWM frequency for the servo motor.
            min_pulse (int): The minimum pulse width in microseconds.
            max_pulse (int): The maximum pulse width in microseconds.
            actuation_range (int): The range of motion of the servo in degrees.
            serial_communication (SerialCommunication): An instance of SerialCommunication for sending messages.
        """
        # Setup PWM output for the servo motor
        self.__servo_pwm = PWMOut(servo_pin, duty_cycle=0, frequency=frequency)
        self.__servo_motor = Servo(self.__servo_pwm, actuation_range=actuation_range,
                                        min_pulse=min_pulse, max_pulse=max_pulse)

        # If serial communication is provided, set it
        self.__serial_communication = serial_communication

        # Set the servo to center position
        self.__angle = self.CENTER_ANGLE
        self.center()

        # Calculate the left and right relative limits
        self.__left_limit = -(self.ACTUATION_RANGE - self.CENTER_ANGLE)
        self.__right_limit = (self.ACTUATION_RANGE - (self.ACTUATION_RANGE - self.CENTER_ANGLE))

    @staticmethod
    def _check_angle(angle: int):
        """
        Checks if the angle is within the valid range.

        Args:
            angle (int): Angle value to check.

        Raises:
            ServoError: If the angle is not within the valid range.
        """
        if not 0 <= angle <= ServoHandler.ACTUATION_RANGE:
            raise ServoError(f"Angle must be between 0 and {ServoHandler.ACTUATION_RANGE} degrees")

    @property
    def angle(self) -> int:
        """
        Returns the current angle of the servo motor.

        Returns:
            int: The current angle of the servo motor.
        """
        return self.__angle

    async def set_angle(self, angle: int):
        """
        Sets the angle of the servo motor.

        Args:
            angle (int): Angle value between 0 and the actuation range.
        """
        # Check if the angle is the same as the current angle
        if angle == self.__angle:
            return

        # Check if the angle is within the valid range
        self._check_angle(angle)
        self.__angle = angle
        self.__servo_motor.angle = self.__angle

        # If serial communication is enabled, send a message with the new angle
        if self.__serial_communication:
            self.__serial_communication.send_message(Message(Category.SERVO, str(self.__angle)))

        # Add a small delay to allow the servo to move
        await sleep(self.DELAY)

    async def set_angle_relative_to_center(self, relative_angle: int):
        """
        Sets the angle of the servo motor relative to the center position.

        Args:
            relative_angle (int): Relative angle value between -90 and 90 degrees.
        """
        if not self.__left_limit <= relative_angle * self.ANGLE_FACTOR <=  self.__right_limit:
            raise ServoError(f"Relative angle must be between {self.__left_limit} and {self.__right_limit} degrees")

        await self.set_angle(self.CENTER_ANGLE + relative_angle * self.ANGLE_FACTOR)

    async def center(self):
        """
        Centers the servo motor to the middle position.
        """
        await self.set_angle(self.CENTER_ANGLE)

    async def right(self, angle):
        """
        Sets the servo motor to the right by a specified angle.

        Args:
            angle (int): Angle value to move the servo to the right, must be between 0 and right limit.
        """
        if not 0 < angle <= self.__right_limit:
            raise ServoError(f"Angle must be between 0 and {self.__right_limit} degrees for right movement")

        await self.set_angle(self.CENTER_ANGLE + angle * self.ANGLE_FACTOR)

    async def left(self, angle):
        """
        Sets the servo motor to the left by a specified angle.

        Args:
            angle (int): Angle value to move the servo to the left, must be between 0 and left limit.
        """
        if not 0 < angle <= abs(self.__left_limit):
            raise ServoError(f"Angle must be between 0 and {abs(self.__left_limit)} degrees for left movement")

        await self.set_angle(self.CENTER_ANGLE - angle * self.ANGLE_FACTOR)

    def is_turning(self):
        """
        Checks if the servo motor is currently turning.

        Returns:
            bool: True if the servo is not centered, False otherwise.
        """
        return self.__angle != self.CENTER_ANGLE