from argparse import ArgumentParser, FileType
from typing import Any, Callable, Optional

from .enums import Flags
from ..constants import VERSIONS, MODELS_NAME
from ..utils import add_single_quotes_to_list_elements

class Args:
    """
    Class to handle command line arguments.
    """

    # Prefix for command line arguments
    PREFIX = '--'

    @classmethod
    def get_attribute_name(cls, attribute: str, disabled: bool = False) -> str:
        """
        Get the attribute name.

        Args:
            attribute (str): The name of the attribute.
            disabled (bool): If True, the attribute will be prefixed with 'no-' to indicate it is disabled.
        Returns:
            str: The attribute name with the prefix.
        """
        return f'{cls.PREFIX}{attribute}' if not disabled else f'{cls.PREFIX}no-{attribute}'

    @staticmethod
    def get_attribute_from_args_dict(args: dict, attribute: str) -> Any:
        """
        Get the attribute name from the args dictionary.

        Args:
            args (dict): The parsed arguments.
            attribute (str): The name of the attribute.
        Returns:
            Any: The value of the attribute from the args.
        """
        # Substitute whitespaces with underscores
        attribute = attribute.replace(' ', '_')

        # Substitute dashes with underscores
        attribute = attribute.replace('-', '_')

        return args[attribute]

    @staticmethod
    def parse_args_as_dict(parser: ArgumentParser) -> dict:
        """
        Parse the arguments and return them as a dictionary.

        Args:
            parser (ArgumentParser): The argument parser instance.
        Returns:
            dict: A dictionary containing the parsed arguments.
        """
        # Parse the arguments
        args = parser.parse_args()

        # Get the arguments as a dictionary
        return vars(args)

    @classmethod
    def _add_boolean_argument(cls, parser: ArgumentParser, flag: Flags, default: bool = False) -> None:
        """
        Add a boolean argument to the parser.

        Args:
            parser (ArgumentParser): The argument parser instance.
            flag (Flags): The flag to be added.
            default (bool): Default value for the boolean argument.
        """
        name = flag.get_flag_name()
        parser.add_argument(cls.get_attribute_name(name, disabled=True), dest=name,
                            action="store_false", help=f"Set {name.lower()} flag as 'False'")
        parser.add_argument(cls.get_attribute_name(name), dest=name,
                            action="store_true", help=f"Set {name.lower()} flag as 'True'")
        parser.set_defaults(**{name: default})

    @classmethod
    def _add_non_boolean_argument(cls, parser: ArgumentParser, flag: Flags, type: Callable[[str], Any] | FileType | str,
                                  default: Optional[Any] = None, required: bool = False,
                                  choices: Optional[list[Any]] = None, help: Optional[str] = None,
                                  nargs: Optional[str] = None) -> None:
        """
        Add a non-boolean argument to the parser.

        Args:
            parser (ArgumentParser): The argument parser instance.
            flag (Flags): The flag to be added.
            type (Callable[[str], Any] | FileType | str): The type of the argument.
            default (Optional[Any]): Default value for the argument.
            required (bool): If True, the argument is required.
            choices (Optional[list[Any]]): List of valid choices for the argument.
            help (Optional[str]): Help text for the argument.
            nargs (Optional[str]): Number of arguments expected.
        """
        name = flag.get_flag_name()
        parser.add_argument(cls.get_attribute_name(name), dest=name, type=type, default=default,
                            required=required, choices=choices, nargs=nargs,
                            help=f"Set {name.lower()} argument" if not help else help)
        
    
    @classmethod
    def add_debug_argument(cls, parser: ArgumentParser, default: bool = False) -> None:
        """
        Add debug argument to the parser.

        Args:
            parser (ArgumentParser): The argument parser to which the argument will be added.
            default (bool): Default value for the debug argument. Defaults to False.
        """
        cls._add_boolean_argument(parser, Flags.DEBUG, default=default)

    @classmethod
    def add_server_argument(cls, parser: ArgumentParser, default: bool = False) -> None:
        """
        Add server argument to the parser.

        Args:
            parser (ArgumentParser): The argument parser instance.
            default (bool): Default value for the server argument.
        """
        cls._add_boolean_argument(parser, Flags.SERVER, default)

    @classmethod
    def add_serial_argument(cls, parser: ArgumentParser, default: bool = False) -> None:
        """
        Add serial argument to the parser.

        Args:
            parser (ArgumentParser): The argument parser instance.
            default (bool): Default value for the serial argument.
        """
        cls._add_boolean_argument(parser, Flags.SERIAL, default)

    @classmethod
    def add_ip_argument(cls, parser: ArgumentParser, default: str = '0.0.0.0') -> None:
        """
        Add IP argument to the parser.

        Args:
            parser (ArgumentParser): The argument parser instance.
            default (str): Default IP address for the server.
        """
        cls._add_non_boolean_argument(parser, Flags.IP, type=str, default=default,
                                      help="Set the IP address for the server")

    @classmethod
    def add_port_argument(cls, parser: ArgumentParser, default: int = 8765) -> None:
        """
        Add port argument to the parser.

        Args:
            parser (ArgumentParser): The argument parser instance.
            default (int): Default port number for the server.
        """
        cls._add_non_boolean_argument(parser, Flags.PORT, type=int, default=default,
                                  choices=[*range(1, 65536)], help="Set the port number for the server")
    
    @classmethod
    def add_yolo_input_model_argument(cls, parser: ArgumentParser) -> None:
        """
        Add YOLO input model argument to the parser.

        Args:
            parser (ArgumentParser): The argument parser to which the argument will be added.
        """
        cls._add_non_boolean_argument(parser, Flags.INPUT_MODEL, type=str, required=True, help='YOLO input model',
                            choices=MODELS_NAME)
        
    @classmethod
    def add_yolo_version_argument(cls, parser: ArgumentParser) -> None:
        """
        Add YOLO version argument to the parser.

        Args:
            parser (ArgumentParser): The argument parser to which the argument will be added.
        """
        cls._add_non_boolean_argument(parser, Flags.VERSION, type=str, required=True, help='YOLO model version',
                                      choices=VERSIONS)
        
    @staticmethod
    def check_model_name(model_name: str) -> None:
        """
        Check the validity of model name.

        Args:
            model_name (str): Name of the YOLO model.
        """
        if model_name not in MODELS_NAME:
            mapped_yolo_models_name = add_single_quotes_to_list_elements(MODELS_NAME)
            raise ValueError(
                f"Invalid model name: {model_name}. Must be one of the following: {', '.join(mapped_yolo_models_name)}.")

    @staticmethod
    def check_yolo_version(yolo_version: str) -> None:
        """
        Check the validity of YOLO version.

        Args:
            yolo_version (str): Version of the YOLO model.
        """
        if yolo_version not in VERSIONS:
            mapped_yolo_versions = add_single_quotes_to_list_elements(VERSIONS)
            raise ValueError(
                f"Invalid yolo version: {yolo_version}. Must be one of the following: {', '.join(mapped_yolo_versions)}.")
