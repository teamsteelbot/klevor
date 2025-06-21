from enum import Enum, unique

@unique
class Flags(Enum):
    """
    Enum to represent command line flags.
    """
    DEBUG = 1
    FORMAT = 2
    QUANTIZED = 3
    INPUT_MODEL = 4
    INPUT_MODEL_PT = 5
    OUTPUT_MODEL = 6
    VERSION = 7
    RETRAINING = 8
    CLASSES = 9
    IGNORE_CLASSES = 10
    EPOCHS = 11
    DEVICE = 12
    IMAGE_SIZE = 13

    def get_flag_name(self) -> str:
        """
        Get the flag name with the prefix.

        Returns:
            str: The flag name with the prefix.
        """
        return self.name.lower().replace("_", "-")