from argparse import ArgumentParser, FileType
from typing import Any, Callable, Optional, List

from .enums import Flag
from .protocols import FlagProtocol
from ..constants import MODELS_NAME, VERSIONS
from ..utils import add_single_quotes_to_list_elements, is_instance


class Args:
	"""
	Class to handle command line arguments.
	"""

	# Prefix for command line arguments
	PREFIX = '--'

	def __init__(self, parser: ArgumentParser):
		"""
		Initialize the Args class with an ArgumentParser instance.

		Args:
			parser (ArgumentParser): The argument parser instance.
		"""
		# Check the type of parser
		is_instance(parser, ArgumentParser)
		self.__parser = parser

		# Initialize the args dictionary
		self.__args: dict[str, Any] = {}

	@staticmethod
	def check_yolo_version(yolo_version: str) -> None:
		"""
		Check the validity of YOLO version.

		Args:
			yolo_version (str): Version of the YOLO model.
		Raises:
			ValueError: If the YOLO version is not valid.
		"""
		if yolo_version not in VERSIONS:
			mapped_yolo_versions = add_single_quotes_to_list_elements(VERSIONS)
			raise ValueError(
				f"Invalid yolo version: {yolo_version}. Must be one of the following: {', '.join(mapped_yolo_versions)}.",
				)

	@staticmethod
	def check_model_name(model_name: str) -> None:
		"""
		Check the validity of model name.

		Args:
			model_name (str): Name of the YOLO model.
		Raises:
			ValueError: If the model name is not valid.
		"""
		if model_name not in MODELS_NAME:
			mapped_yolo_models_name = add_single_quotes_to_list_elements(
				MODELS_NAME,
				)
			raise ValueError(
				f"Invalid model name: {model_name}. Must be one of the following: {', '.join(mapped_yolo_models_name)}.",
				)

	@classmethod
	def _get_attribute_name(
			cls,
			flag: FlagProtocol,
			disabled: bool = False,
			) -> str:
		"""
		Get the attribute name.

		Args:
			flag (FlagProtocol): The flag to get the attribute name for.
			disabled (bool): If True, the attribute will be prefixed with 'no-' to indicate it is disabled.
		Returns:
			str: The attribute name with the prefix.
		"""
		if not disabled:
			return f'{cls.PREFIX}{flag.parsed_name}'
		return f'{cls.PREFIX}no-{flag.parsed_name}'

	def _parse_args_as_dict(self):
		"""
		Parse the arguments and return them as a dictionary.
		"""
		# Parse the arguments
		args = self.__parser.parse_args()

		# Get the arguments as a dictionary
		self.__args = vars(args)

	def _get_attribute_from_args_dict(self, flag: FlagProtocol) -> Any:
		"""
		Get the attribute name from the args dictionary.

		Args:
			flag (FlagProtocol): The flag to get the attribute name for.
		Returns:
			Any: The value of the attribute from the args.
		Raises:
			KeyError: If the attribute is not found in the args dictionary.
		"""
		# Check if the args have been parsed
		parsed = False
		if not self.__args:
			parsed = True
			self._parse_args_as_dict()

		# Substitute whitespaces with underscores
		attribute = flag.parsed_name.replace(' ', '_')

		# Substitute dashes with underscores
		attribute = attribute.replace('-', '_')

		# Check if the attribute exists in the args dictionary
		if attribute not in self.__args and not parsed:
			# If the attribute does not exist, parse the args again
			self._parse_args_as_dict()

		if attribute not in self.__args:
			raise KeyError(
				f"Attribute '{attribute}' not found as an argument in the parser.",
				)
		return self.__args[attribute]

	def _add_boolean_argument(
			self,
			flag: FlagProtocol,
			default: bool = False,
			) -> None:
		"""
		Add a boolean argument to the parser.

		Args:
			flag (FlagProtocol): The flag to be added.
			default (bool): Default value for the boolean argument.
		"""
		# Add the boolean argument to the parser
		name = flag.parsed_name
		self.__parser.add_argument(
			self._get_attribute_name(flag, disabled=True),
			dest=name,
			action="store_false",
			help=f"Set {name.lower()} flag as 'False'",
			)
		self.__parser.add_argument(
			self._get_attribute_name(flag),
			dest=name,
			action="store_true",
			help=f"Set {name.lower()} flag as 'True'",
			)
		self.__parser.set_defaults(**{name: default})

	def _add_non_boolean_argument(
			self,
			flag: FlagProtocol,
			type: Callable[[str], Any] | FileType | str,
			default: Optional[Any] = None,
			required: bool = False,
			choices: Optional[List[Any]] = None,
			help: Optional[str] = None,
			nargs: Optional[str] = None,
			) -> None:
		"""
		Add a non-boolean argument to the parser.

		Args:
			flag (FlagProtocol): The flag to be added.
			type (Callable[[str], Any] | FileType | str): The type of the argument.
			default (Optional[Any]): Default value for the argument.
			required (bool): If True, the argument is required.
			choices (Optional[List[Any]]): List of valid choices for the argument.
			help (Optional[str]): Help text for the argument.
			nargs (Optional[str]): Number of arguments expected.
		"""
		# Add the non-boolean argument to the parser
		name = flag.parsed_name
		self.__parser.add_argument(
			self._get_attribute_name(flag),
			dest=name,
			type=type,
			default=default,
			required=required,
			choices=choices,
			nargs=nargs,
			help=f"Set {name.lower()} argument" if not help else help,
			)

	def add_debug_argument(
			self,
			default: bool = False,
			) -> None:
		"""
		Add debug argument to the parser.

		Args:
			default (bool): Default value for the debug argument. Defaults to False.
		"""
		self._add_boolean_argument(Flag.DEBUG, default=default)

	def get_debug(self) -> bool:
		"""
		Get the debug argument from the parser.

		Returns:
			bool: The value of the debug argument.
		"""
		return self._get_attribute_from_args_dict(Flag.DEBUG)

	def add_server_argument(
			self,
			default: bool = False,
			) -> None:
		"""
		Add server argument to the parser.

		Args:
			default (bool): Default value for the server argument.
		"""
		self._add_boolean_argument(Flag.SERVER, default)

	def get_server(self):
		"""
		Get the server argument from the parser.

		Returns:
			bool: The value of the server argument.
		"""
		return self._get_attribute_from_args_dict(Flag.SERVER)

	def add_serial_argument(
			self,
			default: bool = False,
			) -> None:
		"""
		Add serial argument to the parser.

		Args:
			default (bool): Default value for the serial argument.
		"""
		self._add_boolean_argument(Flag.SERIAL, default)

	def get_serial(self) -> bool:
		"""
		Get the serial argument from the parser.

		Returns:
			bool: The value of the serial argument.
		"""
		return self._get_attribute_from_args_dict(Flag.SERIAL)

	def add_ip_argument(
			self,
			default: str = '0.0.0.0',
			) -> None:
		"""
		Add IP argument to the parser.

		Args:
			default (str): Default IP address for the server.
		"""
		self._add_non_boolean_argument(
			Flag.IP,
			type=str,
			default=default,
			help="Set the IP address for the server",
			)

	def get_ip(self) -> str:
		"""
		Get the IP argument from the parser.

		Returns:
			str: The value of the IP argument.
		"""
		return self._get_attribute_from_args_dict(Flag.IP)

	def add_port_argument(
			self,
			default: int = 8765,
			) -> None:
		"""
		Add port argument to the parser.

		Args:
			default (int): Default port number for the server.
		"""
		self._add_non_boolean_argument(
			Flag.PORT,
			type=int,
			default=default,
			choices=[*range(1, 65536)],
			help="Set the port number for the server",
			)

	def get_port(self) -> int:
		"""
		Get the port argument from the parser.

		Returns:
			int: The value of the port argument.
		"""
		return self._get_attribute_from_args_dict(Flag.PORT)

	def add_yolo_input_model_argument(self) -> None:
		"""
		Add YOLO input model argument to the parser.
		"""
		self._add_non_boolean_argument(
			Flag.INPUT_MODEL,
			type=str,
			required=True,
			help='YOLO input model',
			choices=MODELS_NAME,
			)

	def get_yolo_input_model(self) -> str:
		"""
		Get the YOLO input model argument from the parser.

		Returns:
			str: The value of the YOLO input model argument.
		"""
		return self._get_attribute_from_args_dict(Flag.INPUT_MODEL)

	def add_yolo_version_argument(self) -> None:
		"""
		Add YOLO version argument to the parser.
		"""
		self._add_non_boolean_argument(
			Flag.VERSION,
			type=str,
			required=True,
			help='YOLO model version',
			choices=VERSIONS,
			)

	def get_yolo_version(self) -> str:
		"""
		Get the YOLO version argument from the parser.

		Returns:
			str: The value of the YOLO version argument.
		"""
		return self._get_attribute_from_args_dict(Flag.VERSION)

	def add_movement_argument(
			self,
			default: bool = True,
			) -> None:
		"""
		Add movement argument to the parser.

		Args:
			default (bool): Default value for the movement argument.
		"""
		self._add_boolean_argument(Flag.MOVEMENT, default=default)

	def get_movement(self) -> bool:
		"""
		Get the movement argument from the parser.

		Returns:
			bool: The value of the movement argument.
		"""
		return self._get_attribute_from_args_dict(Flag.MOVEMENT)

	def add_rplidar_is_upside_down_argument(
			self,
			default: bool = False,
			) -> None:
		"""
		Add RPLidar upside down argument to the parser.

		Args:
			default (bool): Default value for the RPLidar upside down argument.
		"""
		self._add_boolean_argument(Flag.RPLIDAR_IS_UPSIDE_DOWN, default=default)

	def get_rplidar_is_upside_down(self) -> bool:
		"""
		Get the RPLidar upside down argument from the parser.

		Returns:
			bool: The value of the RPLidar upside down argument.
		"""
		return self._get_attribute_from_args_dict(Flag.RPLIDAR_IS_UPSIDE_DOWN)

	def add_rplidar_angle_rotation_argument(
			self,
			default: float = 0.0,
			) -> None:
		"""
		Add RPLidar angle rotation argument to the parser.

		Args:
			default (float): Default value for the RPLidar angle rotation
			argument.
		"""
		self._add_non_boolean_argument(
			Flag.RPLIDAR_ANGLE_ROTATION,
			type=float,
			default=default,
			help='RPLidar angle rotation in degrees',
			)

	def get_rplidar_angle_rotation(self) -> float:
		"""
		Get the RPLidar angle rotation argument from the parser.

		Returns:
			float: The value of the RPLidar angle rotation argument.
		"""
		return self._get_attribute_from_args_dict(Flag.RPLIDAR_ANGLE_ROTATION)
