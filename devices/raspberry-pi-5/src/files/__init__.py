import os
import shutil
from datetime import datetime as dt
from typing import LiteralString

class Files:
    """
    Files utility class.
    """
    # Folders (executed from root folder)
    CWD = os.getcwd()

    # Environments
    ENVIRONMENT_LOCAL = "local"
    ENVIRONMENT_COLAB = "colab"

    # Directories to ignore always
    IGNORE_DIRS = ('.git', '__pycache__', '.idea', '.vscode', '.venv', 'venv', 'env')

    # Logs folders
    LOG_DIR = os.path.join(CWD, 'log')
    LOGS_DIR = os.path.join(LOG_DIR, 'logs')

    @staticmethod
    def move_file(input_path: str, output_dir: str) -> None:
        """
        Move file between folders.

        Args:
            input_path (str): The path of the file to be moved.
            output_dir (str): The directory where the file should be moved.
        """
        if os.path.exists(input_path):
            shutil.move(input_path, output_dir)

    @staticmethod
    def move_folder(input_dir: str, output_dir: str) -> None:
        """
        Move folder between folders.

        Args:
            input_dir (str): The path of the folder to be moved.
            output_dir (str): The directory where the folder should be moved.
        """
        if os.path.exists(input_dir):
            shutil.move(input_dir, output_dir)

    @classmethod
    def move_folder_content(cls, input_dir: str, output_dir: str) -> None:
        """
        Move folder content to another folder.

        Args:
            input_dir (str): The path of the folder whose content will be moved.
            output_dir (str): The directory where the content should be moved.
        """
        if os.path.exists(input_dir):
            # Check if the output directory exists, if not create it
            cls.ensure_directory_exists(output_dir)

            # Get all files and folders in the input directory
            for item in os.listdir(input_dir):
                item_input_path = os.path.join(input_dir, item)
                item_output_path = os.path.join(output_dir, item)

                # Check if it's a file and the item already exists in the output directory
                if not os.path.isdir(item_input_path) and os.path.exists(item_output_path):
                    # Delete the item if it already exists in the output directory
                    os.remove(item_output_path)

                # Move each item to the output directory
                shutil.move(item_input_path, output_dir)

    @staticmethod
    def copy_file(input_path: str, output_path: str) -> None:
        """
        Copy a file from input path to output path.

        Args:
            input_path (str): The path of the file to be copied.
            output_path (str): The path where the file should be copied.
        """
        if os.path.exists(input_path):
            shutil.copy(input_path, output_path)

    @staticmethod
    def ensure_directory_exists(path: str) -> None:
        """
        Ensure the directory exists, if not create it.

        Args:
            path (str): The path to check and create if it doesn't exist.
        """
        # Check if it contains an extension
        output_dir = os.path.dirname(path) if os.path.splitext(path)[1] else path

        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)

    @staticmethod
    def ensure_file_exists(file_path: str) -> None:
        """
        Ensure the file exists, if not create it.

        Args:
            file_path (str): The path of the file to check and create if it doesn't exist.
        """
        # Ensure the directory exists
        Files.ensure_directory_exists(os.path.dirname(file_path))

        # Create the file if it does not exist
        if not os.path.exists(file_path):
            with open(file_path, 'w'):
                pass


    @staticmethod
    def check_path_exists(path: str) -> bool:
        """
        Check if the path exists.

        Args:
            path (str): The path to check.
        Returns:
            bool: True if the path exists, False otherwise.
        """
        return os.path.exists(path)
    

    @classmethod
    def get_log_file_path(cls) -> LiteralString | str | bytes:
        """
        Get the log file path.

        Returns:
            LiteralString | str | bytes: The path to the log file with the current timestamp.
        """
        # Get the current time formatted as a string
        formatted_time = dt.now().strftime('%Y-%m-%d_%H-%M-%S')

        return os.path.join(cls.LOGS_DIR, f'{formatted_time}.txt')
