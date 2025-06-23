import os
from os import PathLike
from time import time

from .constants import (
    DATASET_ORIGINAL, DATASET_RESIZED, DATASET_TO_PROCESS, DATASET_AUGMENTED,
    DATASET_ORGANIZED,
    DATASET_PROCESSED, DATASET_STATUSES, RUNS, RUNS_OLD, DATA,
    DATASET_CLASSES_TXT,
    DATASET_LABELED, DATASET_GENERAL, BEST_ONNX, HAILO, HAILO_SUITE, HAILO_LIBS,
    NOTEBOOKS,
    HAILO_MODEL_ZOO, COLAB, LOCAL, BEST_PT, WEIGHTS, ZIP, HAILO_CALIB,
    HAILO_LABELS, TF_RECORDS,
    DATASET_NOTES_JSON
)
from ..args import Args
from ..constants import YOLO_DIR
from ..dataset.constants import DATASET_DIR
from ...files import Files as F
from ...utils import add_single_quotes_to_list_elements


class Files(F):
    """
    Files utility class.
    """

    @staticmethod
    def check_dataset_status(dataset_status: str | None) -> None:
        """
        Check the validity of dataset status.

        Args:
            dataset_status (str | None): The dataset status to check.
        """
        if dataset_status:
            if dataset_status not in [DATASET_TO_PROCESS, DATASET_PROCESSED]:
                mapped_yolo_dataset_statuses = add_single_quotes_to_list_elements(
                    DATASET_STATUSES)
                raise ValueError(
                    f"Invalid dataset status: {dataset_status}. Must be one of the following: {', '.join(mapped_yolo_dataset_statuses)}.")

    @staticmethod
    def check_model_dataset_status(dataset_name: str,
                                   dataset_status: str | None) -> None:
        """
        Check the validity of model dataset status.

        Args:
            dataset_name (str): The name of the dataset.
            dataset_status (str | None): The dataset status to check.
        """
        # Check if the dataset name is split by dataset status
        if dataset_status:
            if dataset_name in [DATASET_AUGMENTED, DATASET_ORGANIZED]:
                raise ValueError(
                    f"Invalid dataset path. The dataset name '{dataset_name}' should not be used with dataset status '{dataset_status}'.")

    @classmethod
    def check_dataset_name(cls, dataset_name: str) -> None:
        """
        Check the validity of dataset name.

        Args:
            dataset_name (str): The name of the dataset to check.
        """
        # Check the validity of dataset name
        if dataset_name not in [DATASET_ORIGINAL, DATASET_RESIZED,
                                DATASET_LABELED, DATASET_AUGMENTED,
                                DATASET_ORGANIZED]:
            raise ValueError(
                f"Invalid dataset name: {dataset_name}. Must be one of the defined dataset folders.")

    @classmethod
    def check_model_dataset_name(cls, dataset_name: str,
                                 model_name: str | None) -> None:
        """
        Check the validity of the model dataset name.

        Args:
            dataset_name (str): The name of the dataset.
            model_name (str | None): The name of the model.
        """
        # Check if the dataset name is split by model name
        if model_name:
            if dataset_name in [DATASET_ORIGINAL, DATASET_RESIZED]:
                raise ValueError(
                    f"Invalid dataset path. The dataset name '{dataset_name}' should not be used with model name '{model_name}'.")

        # Check if the dataset name is split by model name
        elif dataset_name not in [DATASET_ORIGINAL, DATASET_RESIZED]:
            raise ValueError(
                f"Invalid dataset path. The dataset name '{dataset_name}' should not be used without a model name.")

    @classmethod
    def get_dataset_model_dir_path(cls, dataset_name: str,
                                   dataset_status: str | None,
                                   model_name: str | None) -> str | PathLike[
        str]:
        """
        Get the dataset model directory path.

        Args:
            dataset_name (str): The name of the dataset.
            dataset_status (str | None): The status of the dataset (e.g., 'to_process', 'processed').
            model_name (str | None): The name of the YOLO model.
        Returns:
            str | PathLike[str]: The path to the dataset model directory.
        """
        # Check the validity of the model name
        if model_name:
            Args.check_model_name(model_name)

        # Check the validity of the dataset status
        if dataset_status:
            cls.check_dataset_status(dataset_status)
            cls.check_model_dataset_status(dataset_name, dataset_status)

        # Check the validity of the dataset name
        cls.check_dataset_name(dataset_name)
        cls.check_model_dataset_name(dataset_name, model_name)

        # Check if the dataset is split by model name
        if dataset_status and model_name:
            return os.path.join(DATASET_DIR, model_name, dataset_name,
                                dataset_status)

        if dataset_status:
            return os.path.join(DATASET_DIR, DATASET_GENERAL, dataset_name,
                                dataset_status)

        if model_name:
            return os.path.join(DATASET_DIR, model_name, dataset_name)

        return os.path.join(DATASET_DIR, DATASET_GENERAL, dataset_name)

    @classmethod
    def get_yolo_version_dir_path(cls, yolo_version: str) -> str | PathLike:
        """
        Get the YOLO version folder path.

        Args:
            yolo_version (str): The version of the YOLO model.
        Returns:
            str | PathLike: The path to the YOLO version folder.
        """
        # Check the validity of the YOLO version
        Args.check_yolo_version(yolo_version)

        return os.path.join(YOLO_DIR, yolo_version)

    @classmethod
    def get_yolo_runs_dir_path(cls, yolo_version: str) -> str | PathLike:
        """
        Get the YOLO runs folder path.

        Args:
            yolo_version (str): The version of the YOLO model.
        Returns:
            str | PathLike: The path to the YOLO runs folder.
        """
        # Get the YOLO version folder path
        yolo_version_dir = cls.get_yolo_version_dir_path(yolo_version)

        return os.path.join(yolo_version_dir, RUNS)

    @classmethod
    def get_yolo_runs_new_name_dir_path(cls,
                                        yolo_version: str) -> str | PathLike:
        """
        Get the YOLO runs folder path with the new name.

        Args:
            yolo_version (str): The version of the YOLO model.
        Returns:
            str | PathLike: The path to the YOLO runs folder with a new name.
        """
        # Get the YOLO version folder path
        yolo_version_dir = cls.get_yolo_version_dir_path(yolo_version)

        # Get the current Unix timestamp
        unix_timestamp = int(time())

        return os.path.join(yolo_version_dir, f'{RUNS}_{unix_timestamp}')

    @classmethod
    def get_yolo_old_runs_dir_path(cls, yolo_version: str) -> str | PathLike:
        """
        Get the YOLO old runs folder path.

        Args:
            yolo_version (str): The version of the YOLO model.
        Returns:
            str | PathLike: The path to the YOLO old runs folder.
        """
        # Get the YOLO version folder path
        yolo_version_dir = cls.get_yolo_version_dir_path(yolo_version)

        return os.path.join(yolo_version_dir, RUNS_OLD)

    @classmethod
    def get_model_runs_dir_path(cls, model_name: str,
                                yolo_version: str) -> str | PathLike:
        """
        Get the model runs path.

        Args:
            model_name (str): Name of the YOLO model.
            yolo_version (str): Version of the YOLO model.
        Returns:
            str | PathLike: The path to the model runs folder.
        """
        # Get the YOLO runs folder path
        yolo_runs_dir = cls.get_yolo_runs_dir_path(yolo_version)

        # Check the validity of the model name
        Args.check_model_name(model_name)

        return os.path.join(yolo_runs_dir, model_name)

    @classmethod
    def get_model_weight_dir_path(cls, model_name: str,
                                  yolo_version: str) -> str | PathLike:
        """
        Get the model weights path.

        Args:
            model_name (str): Name of the YOLO model.
            yolo_version (str): Version of the YOLO model.
        Returns:
            str | PathLike: The path to the model weights folder.
        """
        # Get the model runs path
        model_runs_path = cls.get_model_runs_dir_path(model_name, yolo_version)

        return os.path.join(model_runs_path, WEIGHTS)

    @classmethod
    def get_model_best_pt_path(cls, model_name: str,
                               yolo_version: str) -> str | PathLike:
        """
        Get the model best PyTorch path.

        Args:
            model_name (str): Name of the YOLO model.
            yolo_version (str): Version of the YOLO model.
        Returns:
            str | PathLike: The path to the model best PyTorch file.
        """
        # Get the model weight path
        model_weight_path = cls.get_model_weight_dir_path(model_name,
                                                          yolo_version)

        return os.path.join(model_weight_path, BEST_PT)

    @classmethod
    def get_model_best_onnx_path(cls, model_name: str,
                                 yolo_version: str) -> str | PathLike:
        """
        Get  the model best ONNX path.

        Args:
            model_name (str): Name of the YOLO model.
            yolo_version (str): Version of the YOLO model.
        Returns:
            str | PathLike: The path to the model best ONNX file.
        """
        # Get the model weight path
        model_weight_path = cls.get_model_weight_dir_path(model_name,
                                                          yolo_version)

        return os.path.join(model_weight_path, BEST_ONNX)

    @classmethod
    def get_yolo_zip_dir_path(cls, yolo_version: str) -> str | PathLike:
        """
        Get the YOLO zip folder path.

        Args:
            yolo_version (str): The version of the YOLO model.
        Returns:
            str | PathLike: The path to the YOLO zip folder.
        """
        # Check the validity of the YOLO version
        Args.check_yolo_version(yolo_version)

        return os.path.join(YOLO_DIR, yolo_version, ZIP)

    @classmethod
    def get_yolo_data_dir_path(cls) -> str | PathLike:
        """
        Get the YOLO data folder path.

        Returns:
            str | PathLike: The path to the YOLO data folder.
        """
        return os.path.join(YOLO_DIR, DATA)

    @classmethod
    def get_yolo_colab_data_dir_path(cls) -> str | PathLike:
        """
        Get the YOLO colab data folder path.

        Returns:
            str | PathLike: The path to the YOLO colab data folder.
        """
        # Get the model data folder path
        yolo_data_dir = cls.get_yolo_data_dir_path()

        return os.path.join(yolo_data_dir, COLAB)

    @classmethod
    def get_yolo_local_data_dir_path(cls) -> str | PathLike:
        """
        Get the YOLO local data folder path.

        Returns:
            str | PathLike: The path to the YOLO local data folder.
        """
        # Get the model data folder path
        yolo_data_dir = cls.get_yolo_data_dir_path()

        return os.path.join(yolo_data_dir, LOCAL)

    @classmethod
    def get_model_data_name(cls, model_name: str) -> str:
        """
        Get the model data name.

        Args:
            model_name (str): Name of the YOLO model.
        Returns:
            str: The name of the model data file.
        """
        # Check the validity of the model name
        Args.check_model_name(model_name)

        return model_name + '.yaml'

    @classmethod
    def get_model_colab_data_path(cls, model_name: str) -> str | PathLike:
        """
        Get the model Colab data path.

        Args:
            model_name (str): Name of the YOLO model.
        Returns:
            str | PathLike: The path to the model Colab data file.
        """
        # Get the model Colab data folder path
        yolo_colab_data_dir = cls.get_yolo_colab_data_dir_path()

        # Get the model data name
        model_data_name = cls.get_model_data_name(model_name)

        return os.path.join(yolo_colab_data_dir, model_data_name)

    @classmethod
    def get_model_local_data_path(cls, model_name: str) -> str | PathLike:
        """
        Get the model local data path.

        Args:
            model_name (str): Name of the YOLO model.
        Returns:
            str | PathLike: The path to the model local data file.
        """
        # Get the model local data folder path
        yolo_local_data_dir = cls.get_yolo_local_data_dir_path()

        # Get the model data name
        model_data_name = cls.get_model_data_name(model_name)

        return os.path.join(yolo_local_data_dir, model_data_name)

    @classmethod
    def get_yolo_notebooks_dir_path(cls, yolo_version: str) -> str | PathLike:
        """
        Get the YOLO notebooks folder path.

        Args:
            yolo_version (str): The version of the YOLO model.
        Returns:
            str | PathLike: The path to the YOLO notebooks folder.
        """
        # Check the validity of the YOLO version
        Args.check_yolo_version(yolo_version)

        return os.path.join(YOLO_DIR, yolo_version, NOTEBOOKS)

    @classmethod
    def get_tf_record_path(cls, model_name: str,
                           yolo_version: str) -> str | PathLike:
        """
        Get the TensorFlow Record path.

        Args:
            model_name (str): Name of the YOLO model.
            yolo_version (str): Version of the YOLO model.
        Returns:
            str | PathLike: The path to the TensorFlow Record file.
        """
        # Get the YOLO version folder path
        yolo_version_dir = cls.get_yolo_version_dir_path(yolo_version)

        # Check the validity of the model name
        Args.check_model_name(model_name)

        return os.path.join(yolo_version_dir, TF_RECORDS,
                            model_name + '.tfrecord')

    @classmethod
    def get_yolo_dataset_notes_file_path(cls, dataset_name: str,
                                         dataset_status: str | None,
                                         model_name: str | None) -> str | PathLike:
        """
        Get the YOLO dataset notes file path.

        Args:
            dataset_name (str): The name of the dataset.
            dataset_status (str | None): The status of the dataset (e.g., 'to_process', 'processed').
            model_name (str | None): The name of the YOLO model.
        Returns:
            str | PathLike: The path to the YOLO dataset notes file.
        """
        # Get the dataset model directory path
        dataset_model_dir_path = cls.get_dataset_model_dir_path(dataset_name,
                                                                dataset_status,
                                                                model_name)

        return os.path.join(dataset_model_dir_path, DATASET_NOTES_JSON)

    @classmethod
    def get_yolo_dataset_classes_file_path(cls, dataset_name: str,
                                           dataset_status: str | None,
                                           model_name: str | None) -> str | PathLike:
        """
        Get the YOLO dataset classes file path.

        Args:
            dataset_name (str): The name of the dataset.
            dataset_status (str | None): The status of the dataset (e.g., 'to_process', 'processed').
            model_name (str | None): The name of the YOLO model.
        Returns:
            str | PathLike: The path to the YOLO dataset classes file.
        """
        # Get the dataset model directory path
        dataset_model_dir_path = cls.get_dataset_model_dir_path(dataset_name,
                                                                dataset_status,
                                                                model_name)

        return os.path.join(dataset_model_dir_path, DATASET_CLASSES_TXT)
