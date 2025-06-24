import os
import time

import torch
from ultralytics import YOLO

from ..files import Files


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
    def run_inference(
        model: YOLO,
        preprocessed_image: torch.Tensor
    ) -> tuple[list, float]:
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
