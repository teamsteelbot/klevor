from enum import Enum, unique


@unique
class Category(Enum):
    """
    Enum to define the category of log message.
    """

    INFO = 1
    WARNING = 2
    ERROR = 3
    DEBUG = 4
