import os
from os import PathLike
from time import time

from ...files import Files as F
from ...utils import add_single_quotes_to_list_elements
from .. import Yolo


class Files(F):
    """
    Files utility class.
    """
    # YOLO folder
    YOLO_DIR = os.path.abspath(os.path.join(F.ROOT_DIR, 'yolo'))

    # YOLO data
    DATA = 'data'

    # YOLO dataset folders
    DATASET_DIR = os.path.abspath(os.path.join(YOLO_DIR, 'dataset'))
    DATASET_GENERAL = 'general'
    DATASET_ORIGINAL = 'original'
    DATASET_RESIZED = 'resized'
    DATASET_LABELED = 'labeled'
    DATASET_AUGMENTED = 'augmented'
    DATASET_ORGANIZED = 'organized'
    DATASET_IMAGES = 'images'
    DATASET_LABELS = 'labels'
    DATASET_TRAINING = 'train'
    DATASET_VALIDATIONS = 'val'
    DATASET_TESTING = 'test'
    DATASET_ANNOTATIONS_JSON = 'annotations.json'
    DATASET_CLASSES_TXT = 'classes.txt'
    DATASET_NOTES_JSON = 'notes.json'
    DATASET_IMAGES_EXT = '.jpg'

    # YOLO dataset status folders
    DATASET_TO_PROCESS = 'to_process'
    DATASET_PROCESSED = 'processed'
    DATASET_STATUSES = (DATASET_TO_PROCESS, DATASET_PROCESSED)

    # YOLO colab
    COLAB = 'colab'

    # YOLO local
    LOCAL = 'local'

    # YOLO notebooks
    NOTEBOOKS = 'notebooks'

    # YOLO Hailo-related folders
    HAILO = 'hailo'
    HAILO_LABELS = 'labels'
    HAILO_CALIB = 'calib'
    HAILO_SUITE = 'suite'
    HAILO_LIBS = 'libs'
    HAILO_MODEL_ZOO = 'hailo_model_zoo'

    # YOLO models
    BEST = 'best'
    BEST_ONNX = 'best.onnx'
    BEST_PT = 'best.pt'
    BEST_TENSOR_RT_QUANTIZED = 'best.engine'
    LAST = 'last'

    # TF Records
    TF_RECORDS = 'tf_records'

    # YOLO runs
    RUNS_OLD = 'runs_old'
    RUNS = 'runs'

    # YOLO weights
    WEIGHTS = 'weights'

    # YOLO zip folder
    ZIP = 'zip'

    # Ignore lists
    ZIP_IGNORE = ('.git', '.venv', '.idea', 'raspberry-pi-pico2', 'scripts', 'yolo')

    @classmethod
    def check_dataset_status(cls, dataset_status: str | None) -> None:
        """
        Check the validity of dataset status.

        Args:
            dataset_status (str | None): The dataset status to check.
        """
        if dataset_status:
            if dataset_status not in [cls.DATASET_TO_PROCESS, cls.DATASET_PROCESSED]:
                mapped_yolo_dataset_statuses = add_single_quotes_to_list_elements(cls.DATASET_STATUSES)
                raise ValueError(
                    f"Invalid dataset status: {dataset_status}. Must be one of the following: {', '.join(mapped_yolo_dataset_statuses)}.")

    @classmethod
    def check_model_dataset_status(cls, dataset_name: str, dataset_status: str | None) -> None:
        """
        Check the validity of model dataset status.

        Args:
            dataset_name (str): The name of the dataset.
            dataset_status (str | None): The dataset status to check.
        """
        # Check if the dataset name is split by dataset status
        if dataset_status:
            if dataset_name in [cls.DATASET_AUGMENTED, cls.DATASET_ORGANIZED]:
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
        if dataset_name not in [cls.DATASET_ORIGINAL, cls.DATASET_RESIZED, cls.DATASET_LABELED, cls.DATASET_AUGMENTED,
                                cls.DATASET_ORGANIZED]:
            raise ValueError(f"Invalid dataset name: {dataset_name}. Must be one of the defined dataset folders.")

    @classmethod
    def check_model_dataset_name(cls, dataset_name: str, model_name: str | None) -> None:
        """
        Check the validity of the model dataset name.

        Args:
            dataset_name (str): The name of the dataset.
            model_name (str | None): The name of the model.
        """
        # Check if the dataset name is split by model name
        if model_name:
            if dataset_name in [cls.DATASET_ORIGINAL, cls.DATASET_RESIZED]:
                raise ValueError(
                    f"Invalid dataset path. The dataset name '{dataset_name}' should not be used with model name '{model_name}'.")

        # Check if the dataset name is split by model name
        elif dataset_name not in [cls.DATASET_ORIGINAL, cls.DATASET_RESIZED]:
            raise ValueError(
                f"Invalid dataset path. The dataset name '{dataset_name}' should not be used without a model name.")

    @classmethod
    def get_dataset_model_dir_path(cls, dataset_name: str, dataset_status: str | None,
                                   model_name: str | None) -> str | PathLike[str]:
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
            Yolo.check_model_name(model_name)

        # Check the validity of the dataset status
        if dataset_status:
            cls.check_dataset_status(dataset_status)
            cls.check_model_dataset_status(dataset_name, dataset_status)

        # Check the validity of the dataset name
        cls.check_dataset_name(dataset_name)
        cls.check_model_dataset_name(dataset_name, model_name)

        # Check if the dataset is split by model name
        if dataset_status and model_name:
            return os.path.join(cls.DATASET_DIR, model_name, dataset_name, dataset_status)

        if dataset_status:
            return os.path.join(cls.DATASET_DIR, cls.DATASET_GENERAL, dataset_name, dataset_status)

        if model_name:
            return os.path.join(cls.DATASET_DIR, model_name, dataset_name)

        return os.path.join(cls.DATASET_DIR, cls.DATASET_GENERAL, dataset_name)

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
        Yolo.check_yolo_version(yolo_version)

        return os.path.join(cls.YOLO_DIR, yolo_version)

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

        return os.path.join(yolo_version_dir, cls.RUNS)

    @classmethod
    def get_yolo_runs_new_name_dir_path(cls, yolo_version: str) -> str | PathLike:
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

        return os.path.join(yolo_version_dir, f'{cls.RUNS}_{unix_timestamp}')

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

        return os.path.join(yolo_version_dir, cls.RUNS_OLD)

    @classmethod
    def get_model_runs_dir_path(cls, model_name: str, yolo_version: str) -> str | PathLike:
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
        Yolo.check_model_name(model_name)

        return os.path.join(yolo_runs_dir, model_name)

    @classmethod
    def get_model_weight_dir_path(cls, model_name: str, yolo_version: str) -> str | PathLike:
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

        return os.path.join(model_runs_path, cls.WEIGHTS)

    @classmethod
    def get_model_best_pt_path(cls, model_name: str, yolo_version: str) -> str | PathLike:
        """
        Get the model best PyTorch path.

        Args:
            model_name (str): Name of the YOLO model.
            yolo_version (str): Version of the YOLO model.
        Returns:
            str | PathLike: The path to the model best PyTorch file.
        """
        # Get the model weight path
        model_weight_path = cls.get_model_weight_dir_path(model_name, yolo_version)

        return os.path.join(model_weight_path, cls.BEST_PT)

    @classmethod
    def get_model_best_onnx_path(cls, model_name: str, yolo_version: str) -> str | PathLike:
        """
        Get  the model best ONNX path.

        Args:
            model_name (str): Name of the YOLO model.
            yolo_version (str): Version of the YOLO model.
        Returns:
            str | PathLike: The path to the model best ONNX file.
        """
        # Get the model weight path
        model_weight_path = cls.get_model_weight_dir_path(model_name, yolo_version)

        return os.path.join(model_weight_path, cls.BEST_ONNX)

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
        Yolo.check_yolo_version(yolo_version)

        return os.path.join(cls.YOLO_DIR, yolo_version, cls.ZIP)

    @classmethod
    def get_yolo_data_dir_path(cls) -> str | PathLike:
        """
        Get the YOLO data folder path.

        Returns:
            str | PathLike: The path to the YOLO data folder.
        """
        return os.path.join(cls.YOLO_DIR, cls.DATA)

    @classmethod
    def get_yolo_colab_data_dir_path(cls) -> str | PathLike:
        """
        Get the YOLO colab data folder path.

        Returns:
            str | PathLike: The path to the YOLO colab data folder.
        """
        # Get the model data folder path
        yolo_data_dir = cls.get_yolo_data_dir_path()

        return os.path.join(yolo_data_dir, cls.COLAB)

    @classmethod
    def get_yolo_local_data_dir_path(cls) -> str | PathLike:
        """
        Get the YOLO local data folder path.

        Returns:
            str | PathLike: The path to the YOLO local data folder.
        """
        # Get the model data folder path
        yolo_data_dir = cls.get_yolo_data_dir_path()

        return os.path.join(yolo_data_dir, cls.LOCAL)

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
        Yolo.check_model_name(model_name)

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
        Yolo.check_yolo_version(yolo_version)

        return os.path.join(cls.YOLO_DIR, yolo_version, cls.NOTEBOOKS)

    @classmethod
    def get_tf_record_path(cls, model_name: str, yolo_version: str) -> str | PathLike:
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
        Yolo.check_model_name(model_name)

        return os.path.join(yolo_version_dir, cls.TF_RECORDS, model_name + '.tfrecord')

    @classmethod
    def get_yolo_dataset_notes_file_path(cls, dataset_name: str, dataset_status: str | None,
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
        dataset_model_dir_path = cls.get_dataset_model_dir_path(dataset_name, dataset_status, model_name)

        return os.path.join(dataset_model_dir_path, Files.DATASET_NOTES_JSON)

    @classmethod
    def get_yolo_dataset_classes_file_path(cls, dataset_name: str, dataset_status: str | None,
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
        dataset_model_dir_path = cls.get_dataset_model_dir_path(dataset_name, dataset_status, model_name)

        return os.path.join(dataset_model_dir_path, Files.DATASET_CLASSES_TXT)

    @classmethod
    def get_hailo_dir_path(cls) -> str | PathLike:
        """
        Get the Hailo folder path.

        Returns:
            str | PathLike: The path to the Hailo folder.
        """
        return os.path.join(cls.YOLO_DIR, cls.HAILO)

    @classmethod
    def get_hailo_suite_dir_path(cls) -> str | PathLike:
        """
        Get the Hailo Suite folder path.

        Returns:
            str | PathLike: The path to the Hailo Suite folder.
        """
        # Get the Hailo folder path
        hailo_dir = cls.get_hailo_dir_path()

        return os.path.join(hailo_dir, cls.HAILO_SUITE)

    @classmethod
    def get_model_hailo_suite_dir_path(cls, model_name: str, yolo_version: str) -> str | PathLike:
        """
        Get the model Hailo Suite path.

        Args:
            model_name (str): Name of the YOLO model.
            yolo_version (str): Version of the YOLO model.
        Returns:
            str | PathLike: The path to the model Hailo Suite folder.
        """
        # Get the Hailo Suite folder path
        hailo_suite_dir = cls.get_hailo_suite_dir_path()

        # Check the validity of the model name
        Yolo.check_model_name(model_name)

        # Check the validity of the YOLO version
        Yolo.check_yolo_version(yolo_version)

        return os.path.join(hailo_suite_dir, yolo_version, model_name)

    @classmethod
    def get_model_hailo_suite_file_path(cls, model_name: str, yolo_version: str,
                                        filename: str) -> str | PathLike:
        """
        Get the model Hailo Suite file path.

        Args:
            model_name (str): Name of the YOLO model.
            yolo_version (str): Version of the YOLO model.
            filename (str): Name of the file to retrieve.
        Returns:
            str | PathLike: The path to the specified file in the model Hailo Suite folder.
        """
        # Get the model Hailo Suite path
        model_hailo_suite_dir = cls.get_model_hailo_suite_dir_path(model_name, yolo_version)

        return os.path.join(model_hailo_suite_dir, filename)

    @classmethod
    def get_model_hailo_suite_parsed_har_file_name(cls, model_name: str) -> str | PathLike:
        """
        Get the Hailo Suite parsed filename.

        Args:
            model_name (str): Name of the YOLO model.
        Returns:
            str | PathLike: The name of the Hailo Suite parsed file.
        """
        return f'{model_name}_parsed.har'

    @classmethod
    def get_model_hailo_suite_optimized_har_file_name(cls, model_name: str) -> str | PathLike:
        """
        Get the Hailo Suite optimized filename.

        Args:
            model_name (str): Name of the YOLO model.
        Returns:
            str | PathLike: The name of the Hailo Suite optimized file.
        """
        return f'{model_name}_optimized.har'

    @classmethod
    def get_model_hailo_suite_compiled_hef_file_name(cls, model_name: str) -> str | PathLike:
        """
        Get the Hailo Suite compiled filename.

        Args:
            model_name (str): Name of the YOLO model.
        Returns:
            str | PathLike: The name of the Hailo Suite compiled file.
        """
        return f'{model_name}_compiled.hef'

    @classmethod
    def get_model_hailo_suite_parsed_har_file_path(cls, model_name: str,
                                                   yolo_version: str) -> str | PathLike:
        """
        Get the model Hailo Suite parsed file path.

        Args:
            model_name (str): Name of the YOLO model.
            yolo_version (str): Version of the YOLO model.
        Returns:
            str | PathLike: The path to the model Hailo Suite parsed file.
        """
        # Get the model Hailo Suite path
        model_hailo_suite_dir = cls.get_model_hailo_suite_dir_path(model_name, yolo_version)

        # Get the Hailo Suite parsed filename
        model_hailo_suite_parsed_har_file_name = cls.get_model_hailo_suite_parsed_har_file_name(model_name)

        return os.path.join(model_hailo_suite_dir, model_hailo_suite_parsed_har_file_name)

    @classmethod
    def get_model_hailo_suite_optimized_har_file_path(cls, model_name: str,
                                                      yolo_version: str) -> str | PathLike:
        """
        Get the model Hailo Suite optimized file path.

        Args:
            model_name (str): Name of the YOLO model.
            yolo_version (str): Version of the YOLO model.
        Returns:
            str | PathLike: The path to the model Hailo Suite optimized file.
        """
        # Get the model Hailo Suite path
        model_hailo_suite_dir = cls.get_model_hailo_suite_dir_path(model_name, yolo_version)

        # Get the Hailo Suite optimized filename
        model_hailo_suite_optimized_har_file_name = cls.get_model_hailo_suite_optimized_har_file_name(model_name)

        return os.path.join(model_hailo_suite_dir, model_hailo_suite_optimized_har_file_name)

    @classmethod
    def get_model_hailo_suite_compiled_hef_file_path(cls, model_name: str,
                                                     yolo_version: str) -> str | PathLike:
        """
        Get the model Hailo Suite compiled file path.

        Args:
            model_name (str): Name of the YOLO model.
            yolo_version (str): Version of the YOLO model.
        Returns:
            str | PathLike: The path to the model Hailo Suite compiled file.
        """
        # Get the model Hailo Suite path
        model_hailo_suite_dir = cls.get_model_hailo_suite_dir_path(model_name, yolo_version)

        # Get the Hailo Suite compiled filename
        model_hailo_suite_compiled_hef_file_name = cls.get_model_hailo_suite_compiled_hef_file_name(model_name)

        return os.path.join(model_hailo_suite_dir, model_hailo_suite_compiled_hef_file_name)

    @classmethod
    def get_model_weights_parsed_har_file_path(cls, model_name: str, yolo_version: str) -> str | PathLike:
        """
        Get the model weights parsed file path.

        Args:
            model_name (str): Name of the YOLO model.
            yolo_version (str): Version of the YOLO model.
        Returns:
            str | PathLike: The path to the model weights parsed file.
        """
        # Get the model weights directory path
        model_weights_dir = cls.get_model_weight_dir_path(model_name, yolo_version)

        return os.path.join(model_weights_dir, 'parsed.har')

    @classmethod
    def get_model_weights_optimized_har_file_path(cls, model_name: str,
                                                  yolo_version: str) -> str | PathLike:
        """
        Get the model weights optimized file path.

        Args:
            model_name (str): Name of the YOLO model.
            yolo_version (str): Version of the YOLO model.
        Returns:
            str | PathLike: The path to the model weights optimized file.
        """
        # Get the model weights directory path
        model_weights_dir = cls.get_model_weight_dir_path(model_name, yolo_version)

        return os.path.join(model_weights_dir, 'optimized.har')

    @classmethod
    def get_model_weights_compiled_hef_file_path(cls, model_name: str,
                                                 yolo_version: str) -> str | PathLike:
        """
        Get the model weights compiled file path.

        Args:
            model_name (str): Name of the YOLO model.
            yolo_version (str): Version of the YOLO model.
        Returns:
            str | PathLike: The path to the model weights compiled file.
        """
        # Get the model weights directory path
        model_weights_dir = cls.get_model_weight_dir_path(model_name, yolo_version)

        return os.path.join(model_weights_dir, 'compiled.hef')

    @classmethod
    def get_hailo_suite_calib_dir_path(cls) -> str | PathLike:
        """
        Get the Hailo Suite calibration set folder.

        Returns:
            str | PathLike: The path to the Hailo Suite calibration set folder.
        """
        # Get the model Hailo Suite path
        model_hailo_suite_dir = cls.get_hailo_suite_dir_path()

        return os.path.join(model_hailo_suite_dir, cls.HAILO_CALIB)

    @classmethod
    def get_hailo_suite_calib_file_path(cls) -> str | PathLike:
        """
        Get the Hailo Suite calibration set file path.

        Returns:
            str | PathLike: The path to the Hailo Suite calibration set file.
        """
        # Get the Hailo Suite calibration set folder path
        hailo_suite_calib_dir = cls.get_hailo_suite_calib_dir_path()

        return os.path.join(hailo_suite_calib_dir, cls.HAILO_CALIB + '.npy')

    @classmethod
    def get_hailo_model_zoo_dir_path(cls) -> str | PathLike:
        """
        Get the Hailo Model Zoo path

        Returns:
            str | PathLike: The path to the Hailo Model Zoo folder.
        """
        return os.path.join(cls.YOLO_DIR, cls.HAILO, cls.HAILO_SUITE, cls.HAILO_LIBS, cls.HAILO_MODEL_ZOO)

    @classmethod
    def get_hailo_labels_dir_path(cls) -> str | PathLike:
        """
        Get the Hailo labels folder path.

        Returns:
            str | PathLike: The path to the Hailo labels folder.
        """
        # Get the Hailo folder path
        hailo_dir = cls.get_hailo_dir_path()

        return os.path.join(hailo_dir, Files.HAILO_LABELS)

    @classmethod
    def get_hailo_labels_file_path(cls, model_name: str) -> str | PathLike:
        """
        Get the Hailo labels file path.

        Args:
            model_name (str): Name of the YOLO model.
        Returns:
            str | PathLike: The path to the Hailo labels file.
        """
        # Check the validity of the model name
        Yolo.check_model_name(model_name)

        # Get the Hailo labels folder path
        hailo_labels_dir = cls.get_hailo_labels_dir_path()

        return os.path.join(hailo_labels_dir, model_name + '.txt')
