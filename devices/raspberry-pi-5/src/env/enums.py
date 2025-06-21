from enum import Enum, unique

@unique
class Key(Enum):
    """
    Enum for environment variable keys.
    """

    DEBUG = 1
    YOLO_VERSION = 2
    CHALLENGE = 3