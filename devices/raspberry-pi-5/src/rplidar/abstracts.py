from abc import ABC, abstractmethod

from .measure import Measure

class RPLIDARABC(ABC):
    """
    Abstract class to handle RPLIDAR operations.
    """

    @abstractmethod
    def measures(self) -> dict[float, Measure]:
        """
        Returns the distances dictionary containing the measures.

        Returns:
            dict[float, Measure]: A dictionary with angles as keys and Measure objects as values.
        """
        pass

    @abstractmethod
    def _calculate_average_distance(self, angles: list[int]) -> float:
        """
        Calculate the average distance for a given list of angles.

        Args:
            angles (list[int]): List of angles to calculate the average distance for.

        Returns:
            float: The average distance for the specified angles.
        """
        pass

    @abstractmethod
    def _after_rotation(self):
        """
        Method to be called after a full rotation.
        """
        pass

    @abstractmethod
    def _read_output(self):
        """
        Read the output from the RPLIDAR process.
        """
        pass

    @abstractmethod
    def _loop(self):
        """
        Loop to read the output from the RPLIDAR process.
        """
        pass

    @abstractmethod
    def _start(self):
        """
        Clear the stop event to allow the RPLIDAR process to start.
        """
        pass

    @abstractmethod
    def start(self):
        """
        Start the RPLIDAR process.
        """
        pass

    @abstractmethod
    def is_running(self) -> bool:
        """
        Check if the RPLIDAR is running.

        Returns:
            bool: True if the RPLIDAR is running, False otherwise.
        """
        pass

    @abstractmethod
    def _stop(self):
        """
        Stop the RPLIDAR process.
        """
        pass

    @abstractmethod
    def is_stopped(self) -> bool:
        """
        Check if the RPLIDAR is stopped.

        Returns:
            bool: True if the RPLIDAR is stopped, False otherwise.
        """
        pass