from abc import ABC, abstractmethod

from ..common.measure import Measure
from ..log import Logger


class RPLidarABC(ABC):
    """
    Abstract class to handle RPLidar operations.
    """

    @abstractmethod
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
    def _start(self) -> None:
        """
        Start the RPLidar process.

        Raises:
            RuntimeError: If the RPLidar process fails to start.
        """
        pass

    @abstractmethod
    def _stop(self) -> None:
        """
        Stop the RPLidar process.
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
