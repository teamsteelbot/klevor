import os


class Env:
    """
    Environment variables manager class.

    This class provides methods to get environment variables related to debug mode and YOLO version.
    """
    DEBUG = 'DEBUG'
    YOLO_VERSION = 'YOLO_VERSION'

    @classmethod
    def set_debug_mode(cls, debug: bool) -> None:
        """
        Set the debug mode in the environment variable.

        Args:
            debug (bool): True to enable debug mode, False to disable.
        """
        os.environ[cls.DEBUG] = str(debug).lower()

    @classmethod
    def set_yolo_version(cls, version: str) -> None:
        """
        Set the YOLO version in the environment variable.

        Args:
            version (str): The YOLO version to set.
        """
        os.environ[cls.YOLO_VERSION] = version

    @classmethod
    def get_debug_mode(cls) -> bool:
        """
        Get the debug mode from the environment variable.

        Returns True if debug mode is enabled, otherwise False.
        """
        return os.getenv(cls.DEBUG, 'false').lower() == 'true'

    @classmethod
    def get_yolo_version(cls) -> str:
        """
        Get the YOLO version from the environment variable.

        Returns the YOLO version as a string.
        """
        return os.getenv(cls.YOLO_VERSION, 'unknown')
