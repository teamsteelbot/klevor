from asyncio import sleep

import board
from adafruit_motor.servo import Servo
from pwmio import PWMOut


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
    LEFT_LIMIT = -(ACTUATION_RANGE - CENTER_ANGLE)
    RIGHT_LIMIT = (ACTUATION_RANGE - (ACTUATION_RANGE - CENTER_ANGLE))

    # Angle factor to normalize that when subtracting the servo moves to the left, and adding moves to the right
    ANGLE_FACTOR = -1

    # Common angle values
    BIG_TURN_ANGLE = 35
    MEDIUM_TURN_ANGLE = 25
    SMALL_TURN_ANGLE = 15

    # Delay
    DELAY = 0.05

    def __init__(
        self, servo_pin: int = SERVO_PIN, frequency: int = PWM_FREQUENCY,
        min_pulse: int = MIN_PULSE, max_pulse: int = MAX_PULSE,
        actuation_range: int = ACTUATION_RANGE, movement: bool = True
        ):
        """
        Initializes the servo handler with the specified parameters.

        Args:
            servo_pin (int): The GPIO pin for the servo motor.
            frequency (int): The PWM frequency for the servo motor.
            min_pulse (int): The minimum pulse width in microseconds.
            max_pulse (int): The maximum pulse width in microseconds.
            actuation_range (int): The range of motion of the servo in degrees.
            movement (bool): If True, the servo will be controlled for movement; if False, it will not.
        """
        # Setup PWM output for the servo motor
        self.__servo_pwm = PWMOut(servo_pin, duty_cycle=0, frequency=frequency)
        self.__servo_motor = Servo(
            self.__servo_pwm, actuation_range=actuation_range,
            min_pulse=min_pulse, max_pulse=max_pulse
            )

        # Set the movement flag
        self.__movement = movement

        # Set the servo to center position
        self.__angle = self.CENTER_ANGLE
        self.center()

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
            raise ServoError(
                f"Angle must be between 0 and {ServoHandler.ACTUATION_RANGE} degrees"
                )

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
        if self.__movement:
            self.__servo_motor.angle = self.__angle

        # Add a small delay to allow the servo to move
        await sleep(self.DELAY)

    async def set_angle_relative_to_center(self, relative_angle: int):
        """
        Sets the angle of the servo motor relative to the center position.

        Args:
            relative_angle (int): Relative angle value between -90 and 90 degrees.

        Raises:
            ServoError: If the relative angle is not within the left and right limits.
        """
        if not self.LEFT_LIMIT <= relative_angle * self.ANGLE_FACTOR <= self.RIGHT_LIMIT:
            raise ServoError(
                f"Relative angle must be between {self.LEFT_LIMIT} and {self.RIGHT_LIMIT} degrees"
                )

        await self.set_angle(
            self.CENTER_ANGLE + relative_angle * self.ANGLE_FACTOR
            )

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

        Raises:
            ServoError: If the angle is not within the right limit.
        """
        if not 0 < angle <= self.RIGHT_LIMIT:
            raise ServoError(
                f"Angle must be between 0 and {self.RIGHT_LIMIT} degrees for right movement"
                )

        await self.set_angle(self.CENTER_ANGLE + angle * self.ANGLE_FACTOR)

    async def left(self, angle):
        """
        Sets the servo motor to the left by a specified angle.

        Args:
            angle (int): Angle value to move the servo to the left, must be between 0 and left limit.

        Raises:
            ServoError: If the angle is not within the left limit.
        """
        if not 0 < angle <= abs(self.LEFT_LIMIT):
            raise ServoError(
                f"Angle must be between 0 and {abs(self.LEFT_LIMIT)} degrees for left movement"
                )

        await self.set_angle(self.CENTER_ANGLE - angle * self.ANGLE_FACTOR)

    def is_turning(self):
        """
        Checks if the servo motor is currently turning.

        Returns:
            bool: True if the servo is not centered, False otherwise.
        """
        return self.__angle != self.CENTER_ANGLE
