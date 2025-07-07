import os
import shutil
from datetime import datetime as dt
from typing import List

from .constants import (
    HAILO_CALIB,
    HAILO_CALIB_DIR,
    HAILO_LABELS_DIR,
    HAILO_SUITE_DIR,
    LOGS_DIR,
    RUNS,
    WEIGHTS,
    YOLO_DIR,
)
from ..args import Args


class Files:
    """
    Files utility class.
    """

    @staticmethod
    def move_file(
        input_path: str | os.PathLike[str],
        output_dir: str | os.PathLike[str]
    ) -> None:
        """
        Move file between folders.

        Args:
            input_path (str | os.PathLike[str]): The path of the file to be moved.
            output_dir (str | os.PathLike[str]): The directory where the file should be moved.
        """
        if os.path.exists(input_path):
            shutil.move(input_path, output_dir)

    @staticmethod
    def move_folder(
        input_dir: str | os.PathLike[str],
        output_dir: str | os.PathLike[str]
    ) -> None:
        """
        Move folder between folders.

        Args:
            input_dir (str | os.PathLike[str]): The path of the folder to be moved.
            output_dir (str | os.PathLike[str]): The directory where the folder should be moved.
        """
        if os.path.exists(input_dir):
            shutil.move(input_dir, output_dir)

    @classmethod
    def move_folder_content(
        cls,
        input_dir: str | os.PathLike[str],
        output_dir: str | os.PathLike[str]
    ) -> None:
        """
        Move folder content to another folder.

        Args:
            input_dir (str | os.PathLike[str]): The path of the folder whose content will be moved.
            output_dir (str | os.PathLike[str]): The directory where the content should be moved.
        """
        if os.path.exists(input_dir):
            # Check if the output directory exists, if not create it
            cls.ensure_directory_exists(output_dir)

            # Get all files and folders in the input directory
            for item in os.listdir(input_dir):
                item_input_path = os.path.join(input_dir, item)
                item_output_path = os.path.join(output_dir, item)

                # Check if it's a file and the item already exists in the output directory
                if not os.path.isdir(item_input_path) and os.path.exists(
                        item_output_path
                ):
                    # Delete the item if it already exists in the output directory
                    os.remove(item_output_path)

                # Move each item to the output directory
                shutil.move(item_input_path, output_dir)

    @staticmethod
    def copy_file(
        input_path: str | os.PathLike[str],
        output_path: str | os.PathLike[str]
    ) -> None:
        """
        Copy a file from input path to output path.

        Args:
            input_path (str | os.PathLike[str]): The path of the file to be copied.
            output_path (str | os.PathLike[str]): The path where the file should be copied.
        """
        if os.path.exists(input_path):
            shutil.copy(input_path, output_path)

    @staticmethod
    def ensure_directory_exists(path: str | os.PathLike[str]) -> None:
        """
        Ensure the directory exists, if not create it.

        Args:
            path (str | os.PathLike[str]): The path to check and create if it doesn't exist.
        """
        # Check if it contains an extension
        output_dir = os.path.dirname(path) if os.path.splitext(path)[
            1] else path

        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)

    @staticmethod
    def ensure_file_exists(file_path: str | os.PathLike[str]) -> None:
        """
        Ensure the file exists, if not create it.

        Args:
            file_path (str | os.PathLike[str]): The path of the file to check and create if it doesn't exist.
        """
        # Ensure the directory exists
        Files.ensure_directory_exists(os.path.dirname(file_path))

        # Create the file if it does not exist
        if not os.path.exists(file_path):
            with open(file_path, 'w'):
                pass

    @staticmethod
    def check_path_exists(path: str | os.PathLike[str]) -> bool:
        """
        Check if the path exists.

        Args:
            path (str | os.PathLike[str]): The path to check.
        Returns:
            bool: True if the path exists, False otherwise.
        """
        return os.path.exists(path)

    @classmethod
    def get_log_file_path(cls) -> str | os.PathLike[str]:
        """
        Get the log file path.

        Returns:
            str | os.PathLike[str]: The path to the log file with the current timestamp.
        """
        # Get the current time formatted as a string
        formatted_time = dt.now().strftime('%Y-%m-%d_%H-%M-%S')

        return os.path.join(LOGS_DIR, f'{formatted_time}.txt')

    @classmethod
    def get_yolo_version_dir_path(cls, yolo_version: str) -> str | os.PathLike:
        """
        Get the YOLO version folder path.

        Args:
            yolo_version (str): The version of the YOLO model.
        Returns:
            str | os.PathLike: The path to the YOLO version folder.
        """
        # Check the validity of the YOLO version
        Args.check_yolo_version(yolo_version)

        return os.path.join(YOLO_DIR, yolo_version)

    @classmethod
    def get_yolo_runs_dir_path(cls, yolo_version: str) -> str | os.PathLike:
        """
        Get the YOLO runs folder path.

        Args:
            yolo_version (str): The version of the YOLO model.
        Returns:
            str | os.PathLike: The path to the YOLO runs folder.
        """
        # Get the YOLO version folder path
        yolo_version_dir = cls.get_yolo_version_dir_path(yolo_version)

        return os.path.join(yolo_version_dir, RUNS)

    @classmethod
    def get_model_runs_dir_path(
        cls,
        model_name: str,
        yolo_version: str
    ) -> str | os.PathLike:
        """
        Get the model runs path.

        Args:
            model_name (str): Name of the YOLO model.
            yolo_version (str): Version of the YOLO model.
        Returns:
            str | os.PathLike: The path to the model runs folder.
        """
        # Get the YOLO runs folder path
        yolo_runs_dir = cls.get_yolo_runs_dir_path(yolo_version)

        # Check the validity of the model name
        Args.check_model_name(model_name)

        return os.path.join(yolo_runs_dir, model_name)

    @classmethod
    def get_model_weight_dir_path(
        cls,
        model_name: str,
        yolo_version: str
    ) -> str | os.PathLike:
        """
        Get the model weights path.

        Args:
            model_name (str): Name of the YOLO model.
            yolo_version (str): Version of the YOLO model.
        Returns:
            str | os.PathLike: The path to the model weights folder.
        """
        # Get the model runs path
        model_runs_path = cls.get_model_runs_dir_path(model_name, yolo_version)

        return os.path.join(model_runs_path, WEIGHTS)

    @classmethod
    def get_model_hailo_suite_dir_path(
        cls,
        model_name: str,
        yolo_version: str
    ) -> str | os.PathLike[str]:
        """
        Get the model Hailo Suite path.

        Args:
            model_name (str): Name of the YOLO model.
            yolo_version (str): Version of the YOLO model.
        Returns:
            str | os.PathLike[str]: The path to the model Hailo Suite folder.
        """
        # Check the validity of the model name
        Args.check_model_name(model_name)

        # Check the validity of the YOLO version
        Args.check_yolo_version(yolo_version)

        return os.path.join(HAILO_SUITE_DIR, yolo_version, model_name)

    @classmethod
    def get_model_hailo_suite_file_path(
        cls,
        model_name: str,
        yolo_version: str,
        filename: str
    ) -> str | os.PathLike[str]:
        """
        Get the model Hailo Suite file path.

        Args:
            model_name (str): Name of the YOLO model.
            yolo_version (str): Version of the YOLO model.
            filename (str): Name of the file to retrieve.
        Returns:
            str | os.PathLike[str]: The path to the specified file in the model Hailo Suite folder.
        """
        # Get the model Hailo Suite path
        model_hailo_suite_dir = cls.get_model_hailo_suite_dir_path(
            model_name,
            yolo_version
        )

        return os.path.join(model_hailo_suite_dir, filename)

    @classmethod
    def get_model_hailo_suite_parsed_har_file_name(
        cls,
        model_name: str
    ) -> str | os.PathLike[str]:
        """
        Get the Hailo Suite parsed filename.

        Args:
            model_name (str): Name of the YOLO model.
        Returns:
            str | os.PathLike[str]: The name of the Hailo Suite parsed file.
        """
        return f'{model_name}_parsed.har'

    @classmethod
    def get_model_hailo_suite_optimized_har_file_name(
        cls,
        model_name: str
    ) -> str | os.PathLike[str]:
        """
        Get the Hailo Suite optimized filename.

        Args:
            model_name (str): Name of the YOLO model.
        Returns:
            str | os.PathLike[str]: The name of the Hailo Suite optimized file.
        """
        return f'{model_name}_optimized.har'

    @classmethod
    def get_model_hailo_suite_compiled_hef_file_name(
        cls,
        model_name: str
    ) -> str | os.PathLike[str]:
        """
        Get the Hailo Suite compiled filename.

        Args:
            model_name (str): Name of the YOLO model.
        Returns:
            str | os.PathLike[str]: The name of the Hailo Suite compiled file.
        """
        return f'{model_name}_compiled.hef'

    @classmethod
    def get_model_hailo_suite_parsed_har_file_path(
        cls,
        model_name: str,
        yolo_version: str
    ) -> str | os.PathLike[str]:
        """
        Get the model Hailo Suite parsed file path.

        Args:
            model_name (str): Name of the YOLO model.
            yolo_version (str): Version of the YOLO model.
        Returns:
            str | os.PathLike[str]: The path to the model Hailo Suite parsed file.
        """
        # Get the model Hailo Suite path
        model_hailo_suite_dir = cls.get_model_hailo_suite_dir_path(
            model_name,
            yolo_version
        )

        # Get the Hailo Suite parsed filename
        model_hailo_suite_parsed_har_file_name = cls.get_model_hailo_suite_parsed_har_file_name(
            model_name
        )

        return os.path.join(
            model_hailo_suite_dir,
            model_hailo_suite_parsed_har_file_name
        )

    @classmethod
    def get_model_hailo_suite_optimized_har_file_path(
        cls,
        model_name: str,
        yolo_version: str
    ) -> str | os.PathLike[str]:
        """
        Get the model Hailo Suite optimized file path.

        Args:
            model_name (str): Name of the YOLO model.
            yolo_version (str): Version of the YOLO model.
        Returns:
            str | os.PathLike[str]: The path to the model Hailo Suite optimized file.
        """
        # Get the model Hailo Suite path
        model_hailo_suite_dir = cls.get_model_hailo_suite_dir_path(
            model_name,
            yolo_version
        )

        # Get the Hailo Suite optimized filename
        model_hailo_suite_optimized_har_file_name = cls.get_model_hailo_suite_optimized_har_file_name(
            model_name
        )

        return os.path.join(
            model_hailo_suite_dir,
            model_hailo_suite_optimized_har_file_name
        )

    @classmethod
    def get_model_hailo_suite_compiled_hef_file_path(
        cls,
        model_name: str,
        yolo_version: str
    ) -> str | os.PathLike[str]:
        """
        Get the model Hailo Suite compiled file path.

        Args:
            model_name (str): Name of the YOLO model.
            yolo_version (str): Version of the YOLO model.
        Returns:
            str | os.PathLike[str]: The path to the model Hailo Suite compiled file.
        """
        # Get the model Hailo Suite path
        model_hailo_suite_dir = cls.get_model_hailo_suite_dir_path(
            model_name,
            yolo_version
        )

        # Get the Hailo Suite compiled filename
        model_hailo_suite_compiled_hef_file_name = cls.get_model_hailo_suite_compiled_hef_file_name(
            model_name
        )

        return os.path.join(
            model_hailo_suite_dir,
            model_hailo_suite_compiled_hef_file_name
        )

    @classmethod
    def get_model_weights_parsed_har_file_path(
        cls,
        model_name: str,
        yolo_version: str
    ) -> str | os.PathLike[str]:
        """
        Get the model weights parsed file path.

        Args:
            model_name (str): Name of the YOLO model.
            yolo_version (str): Version of the YOLO model.
        Returns:
            str | os.PathLike[str]: The path to the model weights parsed file.
        """
        # Get the model weights directory path
        model_weights_dir = cls.get_model_weight_dir_path(
            model_name,
            yolo_version
        )

        return os.path.join(model_weights_dir, 'parsed.har')

    @classmethod
    def get_model_weights_optimized_har_file_path(
        cls,
        model_name: str,
        yolo_version: str
    ) -> str | os.PathLike[str]:
        """
        Get the model weights optimized file path.

        Args:
            model_name (str): Name of the YOLO model.
            yolo_version (str): Version of the YOLO model.
        Returns:
            str | os.PathLike[str]: The path to the model weights optimized file.
        """
        # Get the model weights directory path
        model_weights_dir = cls.get_model_weight_dir_path(
            model_name,
            yolo_version
        )

        return os.path.join(model_weights_dir, 'optimized.har')

    @classmethod
    def get_model_weights_compiled_hef_file_path(
        cls,
        model_name: str,
        yolo_version: str
    ) -> str | os.PathLike[str]:
        """
        Get the model weights compiled file path.

        Args:
            model_name (str): Name of the YOLO model.
            yolo_version (str): Version of the YOLO model.
        Returns:
            str | os.PathLike[str]: The path to the model weights compiled file.
        """
        # Get the model weights directory path
        model_weights_dir = cls.get_model_weight_dir_path(
            model_name,
            yolo_version
        )

        return os.path.join(model_weights_dir, 'compiled.hef')

    @classmethod
    def get_hailo_suite_calib_file_path(cls) -> str | os.PathLike[str]:
        """
        Get the Hailo Suite calibration set file path.

        Returns:
            str | os.PathLike[str]: The path to the Hailo Suite calibration set file.
        """
        return os.path.join(HAILO_CALIB_DIR, HAILO_CALIB + '.npy')

    @classmethod
    def get_hailo_labels_file_path(cls, model_name: str) -> str | os.PathLike[
        str]:
        """
        Get the Hailo labels file path.

        Args:
            model_name (str): Name of the YOLO model.
        Returns:
            str | os.PathLike[str]: The path to the Hailo labels file.
        """
        # Check the validity of the model name
        Args.check_model_name(model_name)

        return os.path.join(HAILO_LABELS_DIR, model_name + '.txt')

    @staticmethod
    def get_labels_from_txt(labels_path: str | os.PathLike[str]) -> List:
        """
        Load labels from a text file.

        Args:
            labels_path (str | os.PathLike[str]): Path to the labels file.
        Returns:
            List: List of class names.
        Raises:
            ValueError: If the labels file does not exist or is not a text file.
        """
        # Ensure the labels file exists
        Files.ensure_directory_exists(labels_path)

        # Check if it's a text file
        if not labels_path.endswith('.txt'):
            raise ValueError(
                f"Expected a .txt file, but got '{labels_path}' instead"
            )

        # Read the labels from the file
        with open(labels_path, 'r', encoding="utf-8") as f:
            class_names = f.read().splitlines()
        return class_names
