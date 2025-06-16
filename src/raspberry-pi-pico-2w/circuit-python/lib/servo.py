import board
from pwmio import PWMOut
from adafruit_motor.servo import Servo

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
    SERVO_PWM_FREQUENCY = 50
    SERVO_MIN_PULSE = 500
    SERVO_MAX_PULSE = 2500
    SERVO_ACTUATION_RANGE = 180
    SERVO_CENTER_ANGLE = 90

    def __init__(self, servo_pin: int = SERVO_PIN, frequency: int = SERVO_PWM_FREQUENCY,
                    min_pulse: int = SERVO_MIN_PULSE, max_pulse: int = SERVO_MAX_PULSE,
                    actuation_range: int = SERVO_ACTUATION_RANGE):
        """
        Initializes the servo handler with the specified parameters.
        """
        # Setup PWM output for the servo motor
        self.__servo_pwm = PWMOut(servo_pin, duty_cycle=0, frequency=frequency)
        self.__servo_motor = Servo(self.__servo_pwm, actuation_range=actuation_range,
                                        min_pulse=min_pulse, max_pulse=max_pulse)

        # Set the servo to center position
        self.__servo_angle = self.SERVO_CENTER_ANGLE
        self.__servo_motor.angle = self.__servo_angle

    @property
    def angle(self):
        """
        Returns the current angle of the servo motor.
        """
        return self.__servo_angle

    @angle.setter
    def angle(self, angle: int):
        """
        Sets the angle of the servo motor.

        Args:
            angle (int): Angle value between 0 and the actuation range.
        """
        if not 0 <= angle <= self.SERVO_ACTUATION_RANGE:
            raise ServoError(f"Angle must be between 0 and {self.SERVO_ACTUATION_RANGE} degrees")

        self.__servo_motor.angle = angle

    def set_angle_relative_to_center(self, relative_angle: int):
        """
        Sets the angle of the servo motor relative to the center position.

        Args:
            relative_angle (int): Relative angle value between half of the actuation range and its negative counterpart.
        """
        relative_actuation_range = self.SERVO_ACTUATION_RANGE // 2
        if not -relative_actuation_range <= relative_angle <= relative_actuation_range:
            raise ServoError(f"Relative angle must be between {-relative_actuation_range} and {relative_actuation_range} degrees")

        self.angle = self.SERVO_CENTER_ANGLE + relative_angle