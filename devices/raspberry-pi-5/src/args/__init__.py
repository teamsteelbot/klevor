from argparse import ArgumentParser
from enum import Enum, unique

@unique
class Flags(Enum):
    """
    Enum to represent command line flags.
    """
    SERVER = 1
    SERIAL = 2
    IP = 3
    PORT = 4

    def get_flag_name(self) -> str:
        """
        Get the flag name with the prefix.

        Returns:
            str: The flag name with the prefix.
        """
        return self.name.lower()

class Args:
    """
    Class to handle command line arguments.
    """
    ARGS_PREFIX = '--'

    @classmethod
    def get_attribute_name(cls, attribute: str) -> str:
        """
        Get the attribute name.

        Args:
            attribute (str): The name of the attribute.
        Returns:
            str: The attribute name with the prefix.
        """
        return f'{cls.ARGS_PREFIX}{attribute}'

    @staticmethod
    def get_attribute_from_args(args: dict, attribute: str) -> str:
        """
        Get the attribute name from the args.

        Args:
            args (dict): The parsed arguments.
            attribute (str): The name of the attribute.
        Returns:
            str: The value of the attribute from the args.
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

    @staticmethod
    def add_server_argument(parser: ArgumentParser, default: bool = False) -> None:
        """
        Add server argument to the parser.

        Args:
            parser (ArgumentParser): The argument parser instance.
            default (bool): Default value for the server argument.
        """
        flag = Flags.SERVER.get_flag_name()
        parser.add_argument(f"--no-{flag}", dest=flag, action="store_false",
                            help="Set server flag as 'False'")
        parser.add_argument(f"--{flag}", dest=flag, action="store_true",
                            help="Set server flag as 'True'")
        parser.set_defaults(**{flag: default})

    @staticmethod
    def add_serial_argument(parser: ArgumentParser, default: bool = False) -> None:
        """
        Add serial argument to the parser.

        Args:
            parser (ArgumentParser): The argument parser instance.
            default (bool): Default value for the serial argument.
        """
        flag = Flags.SERIAL.get_flag_name()
        parser.add_argument(f"--no-{flag}", dest=flag, action="store_false",
                            help="Set serial flag as 'False'")
        parser.add_argument(f"--{flag}", dest=flag, action="store_true",
                            help="Set serial flag as 'True'")
        parser.set_defaults(**{flag: default})

    @staticmethod
    def add_ip_argument(parser: ArgumentParser, default: str = '0.0.0.0') -> None:
        """
        Add IP argument to the parser.

        Args:
            parser (ArgumentParser): The argument parser instance.
            default (str): Default IP address for the server.
        """
        flag = Flags.IP.get_flag_name()
        parser.add_argument(f"--{flag}", dest=flag, type=str, default=default,
                            help="Set the IP address for the server")

    @staticmethod
    def add_port_argument(parser: ArgumentParser, default: int = 8765) -> None:
        """
        Add port argument to the parser.

        Args:
            parser (ArgumentParser): The argument parser instance.
            default (int): Default port number for the server.
        """
        flag = Flags.PORT.get_flag_name()
        parser.add_argument(f"--{flag}", dest=flag, type=int, default=default,
                            help="Set the port for the server")