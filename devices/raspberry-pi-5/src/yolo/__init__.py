import time

import torch
from ultralytics import YOLO

from ..files import Files
from ..utils import add_single_quotes_to_list_elements


class Yolo:
    """
    Class for YOLO PyTorch model operations.

    This class provides methods to load a YOLO model, get class names, export to various formats,
    and run inference. Also, this class contains constants related to YOLO models, directories, colors, and utility functions
    for checking model names, versions, dataset statuses, and dataset names.
    """

    # ONNX metadata properties class names key
    ONNX_METADATA_CLASS_NAMES_KEY = 'names'

    # Number of augmentations
    NUM_AUGMENTATIONS = 10

    # Colors
    GREEN_COLOR = (68, 214, 44)
    MAGENTA_COLOR = (255, 0, 255)
    RED_COLOR = (238, 39, 55)

    # Epochs
    EPOCHS = 100

    # Image size
    IMAGE_SIZE = 640

    # YOLO model names
    MODEL_M = 'm'
    MODEL_G = 'g'
    MODEL_R = 'r'
    MODELS_NAME = (MODEL_M, MODEL_G, MODEL_R)

    # YOLO class colors
    MODEL_G_COLORS = (GREEN_COLOR,)
    MODEL_M_COLORS = (MAGENTA_COLOR,)
    MODEL_R_COLORS = (RED_COLOR,)
    MODELS_COLORS = {
        MODEL_G: MODEL_G_COLORS,
        MODEL_M: MODEL_M_COLORS,
        MODEL_R: MODEL_R_COLORS,
    }

    # YOLO model versions
    VERSION_11 = 'v11'
    VERSIONS = (VERSION_11)

    # Minimum confidence level and number of random images to test
    MINIMUM_CONFIDENCE_LEVEL = 0.70
    NUMBER_RANDOM_IMAGES = 10

    # YOLO formats
    FORMAT_ONNX = 'onnx'
    FORMAT_TFLITE = 'tflite'
    FORMAT_TENSOR_RT = 'tensor_rt'
    FORMAT_PT = 'pt'
    FORMATS = (FORMAT_ONNX, FORMAT_TFLITE, FORMAT_TENSOR_RT, FORMAT_PT)

    # Allowed image extensions
    IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg')

    # Dataset folders ratio
    TRAINING_RATIO = 0.7
    VALIDATION_RATIO = 0.2

    @staticmethod
    def load(model_path: str, task='detect') -> YOLO:
        """
        Load YOLO PyTorch model.

        Args:
            model_path (str): Path to the YOLO model file.
            task (str): Task type, default is 'detect'.
        Returns:
            YOLO: Loaded YOLO model.
        """
        # Check if the model path exists
        Files.ensure_directory_exists(model_path)

        # Load the model
        return YOLO(model_path, task=task, verbose=True)

    @staticmethod
    def get_class_names(model: YOLO) -> dict[int, str]:
        """
        Get YOLO PyTorch model class names.

        Args:
            model (YOLO): Loaded YOLO model.
        Returns:
            dict[int, str]: Dictionary mapping class indices to class names.
        """
        return model.names

    @staticmethod
    def export_tensor_rt(model: YOLO, quantized: bool = True) -> str:
        """
        Export the model to TensorRT format.

        Args:
            model (YOLO): Loaded YOLO model.
            quantized (bool): Whether to quantize the model, default is True.
        Returns:
            str: Path to the exported TensorRT engine file.
        """
        return model.export(format="engine", int8=quantized)

    @staticmethod
    def export_onnx(model: YOLO) -> str:
        """
        Export the model to ONNX format.

        Args:
            model (YOLO): Loaded YOLO model.
        Returns:
            str: Path to the exported ONNX model file.
        """
        return model.export(format="onnx")

    @staticmethod
    def export_tflite(model: YOLO, quantized: bool = True) -> str:
        """
        Export the model to TFLite format.

        Args:
            model (YOLO): Loaded YOLO model.
            quantized (bool): Whether to quantize the model, default is True.
        Returns:
            str: Path to the exported TFLite model file.
        """
        return model.export(format="tflite", int8=quantized)

    @staticmethod
    def run_inference(model: YOLO, preprocessed_image: torch.Tensor) -> tuple[list, float]:
        """
        Run inference from PyTorch model.

        Args:
            model (YOLO): Loaded YOLO model.
            preprocessed_image (torch.Tensor): Preprocessed image tensor.
        Returns:
            tuple(list, float): Inferences and elapsed time in seconds.
        """
        # Get time
        start_time = time.time()

        # Run inference
        inferences = model(torch.from_numpy(preprocessed_image).float())

        # Get time
        end_time = time.time()
        elapsed_time = end_time - start_time

        return inferences, elapsed_time

    @staticmethod
    def get_labels_from_txt(labels_path: str) -> list:
        """
        Load labels from a text file.

        Args:
            labels_path (str): Path to the labels file.
        Returns:
            list: List of class names.
        """
        # Ensure the labels file exists
        Files.ensure_directory_exists(labels_path)

        # Check if it's a text file
        if not labels_path.endswith('.txt'):
            raise ValueError(f"Expected a .txt file, but got '{labels_path}' instead")

        # Read the labels from the file
        with open(labels_path, 'r', encoding="utf-8") as f:
            class_names = f.read().splitlines()
        return class_names

    @classmethod
    def check_model_name(cls, model_name: str) -> None:
        """
        Check the validity of model name.

        Args:
            model_name (str): Name of the YOLO model.
        """
        if model_name not in cls.MODELS_NAME:
            mapped_yolo_models_name = add_single_quotes_to_list_elements(cls.MODELS_NAME)
            raise ValueError(
                f"Invalid model name: {model_name}. Must be one of the following: {', '.join(mapped_yolo_models_name)}.")

    @classmethod
    def check_yolo_version(cls, yolo_version: str) -> None:
        """
        Check the validity of YOLO version.

        Args:
            yolo_version (str): Version of the YOLO model.
        """
        if yolo_version not in cls.VERSIONS:
            mapped_yolo_versions = add_single_quotes_to_list_elements(cls.MODELS_NAME)
            raise ValueError(
                f"Invalid yolo version: {yolo_version}. Must be one of the following: {', '.join(mapped_yolo_versions)}.")

    @classmethod
    def get_model_classes_color_palette(cls, model_name: str) -> tuple[[int, int, int]] | None:
        """
        Get the model classes color palette.

        Args:
            model_name (str): Name of the YOLO model.
        Returns:
            tuple[tuple[int, int, int]] | None: Dictionary mapping class indices to RGB color tuples.
        """
        # Check the validity of the model name
        cls.check_model_name(model_name)
        return cls.MODELS_COLORS[model_name]
