from enum import Enum, unique

@unique
class Flag(Enum):
    """
    Enum to represent command line flags.
    """

    DEBUG = 1
    INPUT_MODEL = 2
    VERSION = 3
    SERVER = 4
    SERIAL = 5
    IP = 6
    PORT = 7

    @property
    def parsed_name(self) -> str:
        """
        Get the flag name in lowercase.

        Returns:
            str: The flag name in lowercase.
        """
        return self.name.lower()