from abc import ABC, abstractmethod

from .constants import MOTOR_SPEED_RANGE, SERVO_ACTUATION_RANGE
from ..rplidar.enums import Direction
from ..common.measure import Measure
from ..log import Logger


class PilotABC(ABC):
    """
    Abstract class for the Pilot handler.

    This class defines the interface for a Pilot handler, which is responsible for
    controlling the robot's movements.
    """

    @staticmethod
    def _check_motor_speed_half_range(speed: float):
        """
        Check the speed value to ensure it is within the valid half range for ESC motors.
        
        Args:
            speed (float): The speed value to check.

        Raises:
            ValueError: If the speed is not within the valid half range.
        """
        if not (0 < speed <= MOTOR_SPEED_RANGE[1]):
            raise ValueError(
                f"Speed must be between 0 and {MOTOR_SPEED_RANGE[1]}"
            )

    @staticmethod
    def _check_motor_speed_full_range(speed: float):
        """
        Check the speed value to ensure it is within the valid full range for ESC motors.
        
        Args:
            speed (float): The speed value to check.

        Raises:
            ValueError: If the speed is not within the valid full range.
        """
        if not (MOTOR_SPEED_RANGE[0] <= speed <= MOTOR_SPEED_RANGE[1]):
            raise ValueError(
                f"Speed must be between {MOTOR_SPEED_RANGE[0]} and {MOTOR_SPEED_RANGE[1]}"
            )
        
    @abstractmethod
    @property
    def logger(self) -> Logger:
        """
        Get the logger instance for the Pilot.

        Returns:
            Logger: The logger instance.
        """
        pass

    @abstractmethod
    async def _set_motor_speed(self, speed: float):
        """
        Sets the speed of the ESC motor.

        Args:
            speed (float): Speed value between -1.0 (full reverse) and 1.0 (full forward).
        """
        pass

    @abstractmethod
    async def _set_motor_stop(self):
        """
        Sets the speed of the ESC motor to 0.
        """
        pass

    @abstractmethod
    async def _set_motor_forward(self, speed: float):
        """
        Sets the speed of the ESC motor forward.

        Args:
            speed (float): Speed value between 0 and 1.0 (full forward).
        """
        pass

    @abstractmethod
    async def _set_motor_backward(self, speed: float):
        """
        Sets the speed of the ESC motor backward.

        Args:
            speed (float): Speed value between 0 and 1.0 (full backward).
        """
        pass

    @staticmethod
    def _check_servo_angle(angle: int):
        """
        Checks if the servo motor angle is within the valid range.

        Args:
            angle (int): Angle value to check.

        Raises:
            ValueError: If the angle is not within the valid range.
        """
        if not 0 <= angle <= SERVO_ACTUATION_RANGE:
            raise ValueError(
                f"Angle must be between 0 and {SERVO_ACTUATION_RANGE} degrees"
            )

    @abstractmethod
    async def _set_servo_angle(self, angle: int):
        """
        Sets the angle of the servo motor.

        Args:
            angle (int): Angle value between 0 and the actuation range.

        Raises:
            ValueError: If the angle is not within the valid range.
        """
        pass

    @abstractmethod
    async def _set_servo_angle_relative_to_center(self, relative_angle: int):
        """
        Sets the angle of the servo motor relative to the center
        position.

        Args:
            relative_angle (int): Relative angle value between -90 and 90 degrees.

        Raises:
            ValueError: If the relative angle is not within the left and right
            limits.
        """
        pass

    @abstractmethod
    async def _set_servo_to_center(self):
        """
        Centers the servo motor to the middle position.
        """
        pass

    @abstractmethod
    async def _set_servo_to_right(self, angle):
        """
        Sets the servo motor to the right by a specified angle.

        Args:
            angle (int): Angle value to move the servo to the right, must be between 0 and right limit.

        Raises:
            ValueError: If the angle is not within the right limit.
        """
        pass

    @abstractmethod
    async def _set_servo_to_left(self, angle):
        """
        Sets the servo motor to the left by a specified angle.

        Args:
            angle (int): Angle value to move the servo to the left, must be between 0 and left limit.

        Raises:
            ValueError: If the angle is not within the left limit.
        """
        pass

    @abstractmethod
    def _is_servo_turning(self):
        """
        Checks if the servo motor is currently turning.

        Returns:
            bool: True if the servo is not centered, False otherwise.
        """
        pass

    @abstractmethod
    def _get_rplidar_measures(self) -> dict[int, Measure]:
        """
        Gets the RPLidar measures.

        Returns:
            dict[int, Measure]: A dictionary containing the RPLidar measures.
        Raises:
            TimeoutError: If the RPLidar measures cannot be retrieved within a timeout.
        """
        pass

    @abstractmethod
    def _get_rplidar_average_distances(self) -> dict[Direction, float]:
        """
        Gets the average distances from the RPLidar measures.

        Returns:
            dict[Direction, float]: A dictionary containing the average distances for each direction.
        """
        pass

    @abstractmethod
    def _challenge_without_obstacles(self):
        """
        Handles the challenge without obstacles.
        """
        pass

    @abstractmethod
    def _challenge_with_obstacles(self):
        """
        Handles the challenge with obstacles.
        """
        pass

    @abstractmethod
    def run(self):
        """
        Runs the pilot handler.
        """
        pass
