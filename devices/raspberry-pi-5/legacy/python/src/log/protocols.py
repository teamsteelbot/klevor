from typing import Protocol, runtime_checkable

from ..log import Logger


@runtime_checkable
class LoggerConsumerProtocol(Protocol):
	"""
	Protocol for classes that consume a logger instance.
	"""

	@property
	def logger(self) -> Logger:
		"""
		Get the logger instance for the consumer.

		Returns:
			Logger: The logger instance.
		"""
		pass
