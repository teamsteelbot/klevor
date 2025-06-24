from abc import ABC, abstractmethod


class RPLIDARABC(ABC):
    """
    Abstract class to handle RPLIDAR operations.
    """

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
    def _read_output(self):
        """
        Read the output from the RPLIDAR process.
        """
        pass

    @abstractmethod
    def run(self):
        """
        Run the RPLIDAR process.

        Raises:
            ValueError: If the ultra_simple file is not found.
            RuntimeError: If the RPLIDAR process fails to start.
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
    def is_stopped(self) -> bool:
        """
        Check if the RPLIDAR is stopped.

        Returns:
            bool: True if the RPLIDAR is stopped, False otherwise.
        """
        pass
