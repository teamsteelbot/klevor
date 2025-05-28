from argparse import ArgumentParser


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
