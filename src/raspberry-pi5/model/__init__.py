import time

import torch
from ultralytics import YOLO

from files import Files


class Yolo:
    """
    Class for YOLO PyTorch model operations.

    This class provides methods to load a YOLO model, get class names, export to various formats,
    and run inference.
    """

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
        Files.ensure_path_exists(model_path)

        # Load the model
        model = YOLO(model_path, task=task, verbose=True)
        return model

    @staticmethod
    def get_class_names(model: YOLO) -> dict[int, str]:
        """
        Get YOLO PyTorch model class names.

        Args:
            model (YOLO): Loaded YOLO model.
        Returns:
            dict[int, str]: Dictionary mapping class indices to class names.
        """
        # Detected PyTorch model class names
        print(f'Classes: {model.names}')

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
    def run_inference(model: YOLO, preprocessed_image: torch.Tensor) -> list:
        """
        Run inference from PyTorch model.

        Args:
            model (YOLO): Loaded YOLO model.
            preprocessed_image (torch.Tensor): Preprocessed image tensor.
        Returns:
            list: Inference outputs from the model.
        """
        # Get time
        start_time = time.time()

        # Run inference
        inferences = model(torch.from_numpy(preprocessed_image).float())

        # Get time
        end_time = time.time()
        elapsed_time = end_time - start_time

        # Log
        print(f'Inference took {elapsed_time:.2f} seconds')

        return inferences
