from typing import Protocol

from ..log import Logger

class LoggerConsumerProtocol(Protocol):
    """
    Protocol for classes that consume a logger instance.
    """

    def logger(self) -> 'Logger':
        """
        Get the logger instance for the consumer.

        Returns:
            Logger: The logger instance.
        """
        pass