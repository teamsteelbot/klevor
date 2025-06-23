from typing import Protocol


class FlagProtocol(Protocol):
    """
    Protocol for flag classes.
    """

    @property
    def parsed_name(self) -> str:
        """
        Get the parsed name of the flag.
        """
        pass
