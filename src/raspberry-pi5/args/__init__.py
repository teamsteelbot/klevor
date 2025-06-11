from argparse import ArgumentParser


class Args:
    """
    Class to handle command line arguments.
    """
    ARGS_PREFIX = '--'

    # Arguments
    SERVER = 'server'
    SERIAL = 'serial'

    @classmethod
    def get_attribute_name(cls, attribute: str) -> str:
        """
        Get the attribute name.

        Args:
            attribute (str): The name of the attribute.
        """
        return f'{cls.ARGS_PREFIX}{attribute}'

    @staticmethod
    def get_attribute_from_args(args: dict, attribute: str):
        """
        Get the attribute name from the args.

        Args:
            args (dict): The parsed arguments.
            attribute (str): The name of the attribute.
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
    def add_server_argument(cls, parser, default: bool = False) -> None:
        """
        Add server argument to the parser.
        """
        parser.add_argument(f"--no-{cls.SERVER}", dest=cls.SERVER, action="store_false",
                            help="Set server flag as 'False'")
        parser.add_argument(f"--{cls.SERVER}", dest=cls.SERVER, action="store_true",
                            help="Set server flag as 'True'")
        parser.set_defaults(**{cls.SERVER: default})

    @classmethod
    def add_serial_argument(cls, parser, default: bool = False) -> None:
        """
        Add serial argument to the parser.
        """
        parser.add_argument(f"--no-{cls.SERIAL}", dest=cls.SERIAL, action="store_false",
                            help="Set serial flag as 'False'")
        parser.add_argument(f"--{cls.SERIAL}", dest=cls.SERIAL, action="store_true",
                            help="Set serial flag as 'True'")
        parser.set_defaults(**{cls.SERIAL: default})