import os

# Environment variables
ENV_DEBUG = 'DEBUG'
ENV_YOLO_VERSION = 'YOLO_VERSION'

# Get debug mode from environment variable
def get_debug_mode() -> bool:
    """
    Get the debug mode from the environment variable.
    """
    return os.getenv(ENV_DEBUG).lower() == 'true'


# Get YOLO version from environment variable
def get_yolo_version() -> str:
    """
    Get the YOLO version from the environment variable.
    """
    return os.getenv(ENV_YOLO_VERSION)