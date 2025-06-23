from enum import Enum, unique

from ...args.enums import Flag as BaseFlags


@unique
class Flag(Enum):
    """
    Enum to represent command line flags.
    """

    DEBUG = BaseFlags.DEBUG.value
    INPUT_MODEL = BaseFlags.INPUT_MODEL.value
    VERSION = BaseFlags.VERSION.value
    FORMAT = 4
    QUANTIZED = 5
    INPUT_MODEL_PT = 6
    OUTPUT_MODEL = 7
    RETRAINING = 8
    CLASSES = 9
    IGNORE_CLASSES = 10
    EPOCHS = 11
    DEVICE = 12
    IMAGE_SIZE = 13

    @property
    def parsed_name(self) -> str:
        """
        Get the flag name with the prefix.

        Returns:
            str: The flag name with the prefix.
        """
        return self.name.lower().replace("_", "-")
