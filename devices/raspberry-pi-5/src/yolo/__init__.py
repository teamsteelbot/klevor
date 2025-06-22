import os
import time

import torch
from ultralytics import YOLO

from ..constants import MODELS_NAME, MODELS_COLORS
from .constants import VERSIONS
from ..files import Files
from ..utils import add_single_quotes_to_list_elements


class Yolo:
    """
    Class for YOLO PyTorch model operations.

    This class provides methods to load a YOLO model, get class names, export to various formats,
    and run inference. Also, this class contains constants related to YOLO models, directories, colors, and utility functions
    for checking model names, versions, dataset statuses, and dataset names.
    """

    @staticmethod
    def load(model_path: str | os.PathLike[str], task='detect') -> YOLO:
        """
        Load YOLO PyTorch model.

        Args:
            model_path (str | os.PathLike[str]): Path to the YOLO model file.
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
    def get_labels_from_txt(labels_path: str | os.PathLike[str]) -> list:
        """
        Load labels from a text file.

        Args:
            labels_path (str | os.PathLike[str]): Path to the labels file.
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

    @staticmethod
    def check_model_name(model_name: str) -> None:
        """
        Check the validity of model name.

        Args:
            model_name (str): Name of the YOLO model.
        """
        if model_name not in MODELS_NAME:
            mapped_yolo_models_name = add_single_quotes_to_list_elements(MODELS_NAME)
            raise ValueError(
                f"Invalid model name: {model_name}. Must be one of the following: {', '.join(mapped_yolo_models_name)}.")

    @staticmethod
    def check_yolo_version(yolo_version: str) -> None:
        """
        Check the validity of YOLO version.

        Args:
            yolo_version (str): Version of the YOLO model.
        """
        if yolo_version not in VERSIONS:
            mapped_yolo_versions = add_single_quotes_to_list_elements(VERSIONS)
            raise ValueError(
                f"Invalid yolo version: {yolo_version}. Must be one of the following: {', '.join(mapped_yolo_versions)}.")

    @staticmethod
    def get_model_classes_color_palette(model_name: str) -> tuple[tuple[int, int, int]]:
        """
        Get the model classes color palette.

        Args:
            model_name (str): Name of the YOLO model.
        Returns:
            tuple[tuple[int, int, int]]: Tuple mapping class indices to RGB color tuples.
        """
        # Check the validity of the model name
        Yolo.check_model_name(model_name)

        if not model_name in MODELS_COLORS:
            raise ValueError(f"Model name '{model_name}' does not have a defined color palette.")
        return MODELS_COLORS[model_name]
