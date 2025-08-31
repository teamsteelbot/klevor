from enum import Enum, unique

from .utils import map_string_to_enum


@unique
class Challenge(Enum):
	"""
	Enum to represent different challenges.
	"""

	WITH_OBSTACLES = 1
	WITHOUT_OBSTACLES = 2
	NONE = 3

	@classmethod
	def from_string(cls, challenge_str: str) -> 'Challenge':
		"""
		Convert a string to a Challenge enum value.

		Args:
			challenge_str (str): The string representation of the challenge.

		Returns:
			Challenge: The corresponding Challenge enum value.
		"""
		return map_string_to_enum(challenge_str.upper(), cls)

	@property
	def as_char(self) -> str:
		"""
		Get the challenge as a character.

		Returns:
			str: The challenge as a character.
		"""
		if self == Challenge.WITH_OBSTACLES:
			return b'Y'
		elif self == Challenge.WITHOUT_OBSTACLES:
			return b'N'
		elif self == Challenge.NONE:
			return b'n'
