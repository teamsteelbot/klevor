import os

# Environment variables
ENV_DEBUG = 'DEBUG'
ENV_YOLO_VERSION = 'YOLO_VERSION'

# Get debug mode from environment variable
def get_debug_mode() -> bool:
    """
    Get the debug mode from the environment variable.

    Returns True if debug mode is enabled, otherwise False.
    """
    return os.getenv(ENV_DEBUG).lower() == 'true'


# Get YOLO version from environment variable
def get_yolo_version() -> str:
    """
    Get the YOLO version from the environment variable.

    Returns the YOLO version as a string.
    """
    return os.getenv(ENV_YOLO_VERSION)