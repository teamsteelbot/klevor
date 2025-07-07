from abc import ABC, abstractmethod
from typing import Dict
from math import ceil, floor

from .constants import (
    MOTOR_SPEED_RANGE,
    SERVO_ACTUATION_RANGE,
    DIRECTION_TO_ANGLE,
    ANGLE_WIDTH
)
from ..common.measure import Measure
from ..log import Logger
from .enums import Direction


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

    @classmethod
    def _calculate_average_distance_from_angle(
        cls,
        measures: Dict[int, Measure],
        middle_angle: int,
        width: int = ANGLE_WIDTH
    ) -> float:
        """
        Calculate the average distance for a given list of angles.

        Args:
            measures (Dict[int, Measure]): Dictionary of measures indexed by angle.
            middle_angle (int): The middle angle to start the averaging from.
            width (int): The sum of the angles to consider with both sides and the middle angle.
        Returns:
            float: The average distance for the specified angles.
        Raises:
            ValueError: If the width is not an even number or if it is greater than or equal to 360 degrees.
        """
        # Initialize total distance and count
        total_distance = 0.0
        count = 0

        # Calculate the range of angles to consider
        if width % 2 == 0:
            raise ValueError("Width must be an odd number.")
        if width < 1:
            raise ValueError("Width must be greater than 0.")
        if width >= 360:
            raise ValueError("Width must be less than 360 degrees.")

        # Check if the width is 1, in which case we only consider the middle angle
        if width == 1:
            return measures.get(
                middle_angle,
                Measure(middle_angle, 0.0, 0)
                ).distance

        # Calculate the angles to consider
        angles = []
        width_per_side = (width - 1) // 2
        left_angle = middle_angle - width_per_side
        right_angle = middle_angle + width_per_side
        if left_angle < 0:
            angles = [
                *angles,
                *range(360 + left_angle, 360)
            ]
        if right_angle >= 360:
            angles = [
                *angles,
                *range(0, right_angle - 360 + 1)
            ]

        angles = [
            *angles,
            *range(
                max(left_angle, 0),
                min(360, right_angle + 1)
            )
        ]

        for angle in angles:
            measure = measures.get(angle, None)
            if measure is None:
                continue

            # Check the distance and quality
            if measure.distance == 0.0 or measure.quality == 0:
                continue

            total_distance += measure.distance
            count += 1
        return total_distance / count if count > 0 else 0.0

    @classmethod
    def _calculate_average_distance_from_direction(
        cls,
        measures: Dict[int, Measure],
        direction: Direction,
        width: int = ANGLE_WIDTH
    ) -> float:
        """
        Calculate the average distance for a given list of angles.

        Args:
            measures (Dict[int, Measure]): Dictionary of measures indexed by angle.
            width (int): The sum of the angles to consider with both sides and the middle angle.
            direction (Direction): Direction to calculate the average distance for.
        Returns:
            float: The average distance for the specified angles.
        Raises:
            ValueError: If the direction is not valid or no measures are found.
        """
        direction_angle = DIRECTION_TO_ANGLE.get(direction, None)
        if direction_angle is None:
            raise ValueError(f"No angle found for direction: {direction}")

        # Round the angle
        direction_angle = ceil(direction_angle) if direction_angle >= 180 else floor(direction_angle)

        return cls._calculate_average_distance_from_angle(
            measures,
            int(direction_angle),
            width
        )

    @classmethod
    def _calculate_average_distance(
        cls,
        measures: Dict[int, Measure],
        *directions: Direction,
    ) -> Dict[Direction, float]:
        """
        Calculate the average distances for the specified directions.

        Args:
            measures (Dict[int, Measure]): Dictionary of measures indexed by angle.
            *directions (Direction): Directions to calculate the average distances for.
        Returns:
            Dict[Direction, float]: Dictionary with directions as keys and their average distances as values.
        """
        avg_distances = {}
        for direction in directions:
            avg_distances[direction] = cls._calculate_average_distance_from_direction(
                measures, direction
            )
        return avg_distances

    @abstractmethod
    def logger(self) -> Logger:
        """
        Get the logger instance for the Pilot.

        Returns:
            Logger: The logger instance.
        """
        pass

    @abstractmethod
    def _set_motor_speed(self, speed: float):
        """
        Sets the speed of the ESC motor.

        Args:
            speed (float): Speed value between -1.0 (full reverse) and 1.0 (full forward).
        """
        pass

    @abstractmethod
    def _set_motor_stop(self):
        """
        Sets the speed of the ESC motor to 0.
        """
        pass

    @abstractmethod
    def _set_motor_forward(self, speed: float):
        """
        Sets the speed of the ESC motor forward.

        Args:
            speed (float): Speed value between 0 and 1.0 (full forward).
        """
        pass

    @abstractmethod
    def _set_motor_backward(self, speed: float):
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
    def _set_servo_angle(self, angle: int):
        """
        Sets the angle of the servo motor.

        Args:
            angle (int): Angle value between 0 and the actuation range.

        Raises:
            ValueError: If the angle is not within the valid range.
        """
        pass

    @abstractmethod
    def _set_servo_angle_relative_to_center(self, relative_angle: int):
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
    def _set_servo_to_center(self):
        """
        Centers the servo motor to the middle position.
        """
        pass

    @abstractmethod
    def _set_servo_to_right(self, angle: int):
        """
        Sets the servo motor to the right by a specified angle.

        Args:
            angle (int): Angle value to move the servo to the right, must be between 0 and right limit.

        Raises:
            ValueError: If the angle is not within the right limit.
        """
        pass

    @abstractmethod
    def _is_servo_to_right(self) -> bool:
        """
        Check if the servo is in the right position.

        Returns:
            bool: True if the servo is in the right position, False otherwise.
        """
        pass

    @abstractmethod
    def _set_servo_to_left(self, angle: int):
        """
        Sets the servo motor to the left by a specified angle.

        Args:
            angle (int): Angle value to move the servo to the left, must be between 0 and left limit.

        Raises:
            ValueError: If the angle is not within the left limit.
        """
        pass

    @abstractmethod
    def _is_servo_to_right(self) -> bool:
        """
        Check if the servo is in the right position.

        Returns:
            bool: True if the servo is in the right position, False otherwise.
        """
        pass

    @abstractmethod
    def _set_servo_to_opposite(self, angle: int):
        """
        Sets the servo angle to the opposite direction.

        Args:
            angle (int): The angle to set the servo to.
        """
        pass

    @abstractmethod
    def _get_rplidar_measures(self) -> Dict[int, Measure]:
        """
        Gets the RPLidar measures.

        Returns:
            Dict[int, Measure]: A dictionary containing the RPLidar measures.
        Raises:
            TimeoutError: If the RPLidar measures cannot be retrieved within a timeout.
        """
        pass

    @abstractmethod
    def _update_rplidar_average_distances(self) -> None:
        """
        Updates the average distances from the RPLidar measures.
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
    def _start(self):
        """
        Starts the pilot handler.

        Raises:
            RuntimeError: If the pilot handler cannot be started.
        """
        pass

    @abstractmethod
    def _stop(self):
        """
        Stops the pilot handler.
        """
        pass

    @abstractmethod
    def run(self):
        """
        Runs the pilot handler.
        """
        pass
