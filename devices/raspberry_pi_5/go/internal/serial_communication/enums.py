from enum import Enum, unique

from ..utils import map_string_to_enum


@unique
class IncomingCategory(Enum):
	"""
	Enum to represent the categories of incoming messages from the Raspberry Pi Pico 2W.
	"""
	CHALLENGE = 1
	STATUS = 2
	BNO08X_YAW_DEG = 3
	BNO08X_TURNS = 4
	ERROR = 5
	DEBUG = 6

	@property
	def parsed_name(self) -> str:
		"""
		Get the category name in lowercase.

		Returns:
			str: The category name in lowercase.
		"""
		return self.name.lower()

	@classmethod
	def from_string(cls, category_str: str) -> 'IncomingCategory':
		"""
		Convert a string to an IncomingCategory enum value.

		Args:
			category_str (str): The string representation of the incoming category.
		Returns:
			IncomingCategory: The corresponding IncomingCategory enum value.
		"""
		return map_string_to_enum(category_str.upper(), cls)


@unique
class Status(Enum):
	"""
	Enum to represent the status messages sent and received from the Raspberry Pi Pico 2W.
	"""
	START = 1
	STOP = 2
	OK = 3
	HEARTBEAT = 4

	@property
	def parsed_name(self) -> str:
		"""
		Get the status name in lowercase.

		Returns:
			str: The status name in lowercase.
		"""
		return self.name.lower()

	@classmethod
	def from_string(cls, status_str: str) -> 'Status':
		"""
		Convert a string to a Status enum value.

		Args:
			status_str (str): The string representation of the status.
		Returns:
			Status: The corresponding Status enum value.
		"""
		return map_string_to_enum(status_str.upper(), cls)


@unique
class OutgoingCategory(Enum):
	"""
	Enum to represent the categories of outgoing messages sent to the Raspberry Pi Pico 2W.
	"""
	STATUS = 1
	SERVO_ANGLE = 2
	MOTOR_SPEED = 3

	@property
	def parsed_name(self) -> str:
		"""
		Get the category name in lowercase.

		Returns:
			str: The category name in lowercase.
		"""
		return self.name.lower()

	@classmethod
	def from_string(cls, category_str: str) -> 'OutgoingCategory':
		"""
		Convert a string to an OutgoingCategory enum value.

		Args:
			category_str (str): The string representation of the outgoing category.
		Returns:
			OutgoingCategory: The corresponding OutgoingCategory enum value.
		"""
		return map_string_to_enum(category_str.upper(), cls)
