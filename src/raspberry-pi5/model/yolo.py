import os
import time
from pathlib import Path

import torch
from ultralytics import YOLO


def load(model: str, task='detect') -> YOLO:
    """
    Load YOLO PyTorch model.

    Args:
        model (str): Path to the YOLO model file.
        task (str): Task type, default is 'detect'.
    Returns:
        YOLO: Loaded YOLO model.
    """
    # Check if the model has a parent directory
    if Path(model).parent != Path('.'):
        # Verify the model file exists
        if not os.path.exists(model):
            raise FileNotFoundError(f"Model file not found: {model}")

    # Load the model
    model = YOLO(model, task=task, verbose=True)
    return model

def get_class_names(model: YOLO)-> dict[int, str]:
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

def export_tensor_rt(model: YOLO, quantized: bool = True)-> str:
    """
    Export the model to TensorRT format.

    Args:
        model (YOLO): Loaded YOLO model.
        quantized (bool): Whether to quantize the model, default is True.
    Returns:
        str: Path to the exported TensorRT engine file.
    """
    return model.export(format="engine", int8=quantized)

def export_onnx(model: YOLO)-> str:
    """
    Export the model to ONNX format.

    Args:
        model (YOLO): Loaded YOLO model.
    Returns:
        str: Path to the exported ONNX model file.
    """
    return model.export(format="onnx")

def export_tflite(model: YOLO, quantized: bool = True)-> str:
    """
    Export the model to TFLite format.

    Args:
        model (YOLO): Loaded YOLO model.
        quantized (bool): Whether to quantize the model, default is True.
    Returns:
        str: Path to the exported TFLite model file.
    """
    return model.export(format="tflite", int8=quantized)

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
    outputs = model(torch.from_numpy(preprocessed_image).float())

    # Get time
    end_time = time.time()
    elapsed_time = end_time - start_time

    # Log
    print(f'Inference took {elapsed_time:.2f} seconds')

    return outputs
