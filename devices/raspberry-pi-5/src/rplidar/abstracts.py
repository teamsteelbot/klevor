from abc import ABC, abstractmethod

from ..common.measure import Measure
from ..log import Logger


class RPLidarABC(ABC):
    """
    Abstract class to handle RPLidar operations.
    """

    @staticmethod
    def calculate_average_distance(
        measures: dict[int, Measure],
        angles: list[int]
    ) -> float:
        """
        Calculate the average distance for a given list of angles.

        Args:
            angles (list[int]): List of angles to calculate the average distance for.

        Returns:
            float: The average distance for the specified angles.
        """
        total_distance = 0.0
        count = 0
        for angle in angles:
            if angle in measures:
                total_distance += measures[angle].distance
                count += 1
        return total_distance / count if count > 0 else 0.0

    @abstractmethod
    @property
    def logger(self) -> Logger:
        """
        Get the logger instance for the RPLidar.

        Returns:
            Logger: The logger instance.
        """
        pass

    @abstractmethod
    def _read_output(self):
        """
        Read the output from the RPLidar process.
        """
        pass

    @abstractmethod
    def run(self):
        """
        Run the RPLidar process.

        Raises:
            ValueError: If the ultra_simple file is not found.
            RuntimeError: If the RPLidar process fails to start.
        """
        pass

    @abstractmethod
    def is_running(self) -> bool:
        """
        Check if the RPLidar is running.

        Returns:
            bool: True if the RPLidar is running, False otherwise.
        """
        pass

    @abstractmethod
    def is_stopped(self) -> bool:
        """
        Check if the RPLidar is stopped.

        Returns:
            bool: True if the RPLidar is stopped, False otherwise.
        """
        pass
