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