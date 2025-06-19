from abc import ABC, abstractmethod

class RPLIDARABC(ABC):
    """
    Abstract class to handle RPLIDAR operations.
    """

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