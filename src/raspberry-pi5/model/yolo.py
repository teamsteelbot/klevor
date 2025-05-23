import os
import time
from pathlib import Path

import torch
from ultralytics import YOLO


def load(model: str, task='detect'):
    """
    Load YOLO PyTorch model.
    """
    # Check if the model has a parent directory
    if Path(model).parent != Path('.'):
        # Verify the model file exists
        if not os.path.exists(model):
            raise FileNotFoundError(f"Model file not found: {model}")

    # Load the model
    model = YOLO(model, task=task, verbose=True)
    return model

def get_class_names(model):
    """
    Get YOLO PyTorch model class names.
    """
    # Detected PyTorch model class names
    print(f'Classes: {model.names}')

    return model.names

def export_tensor_rt(model, quantized: bool = True):
    """
    Export the model to TensorRT format.
    """
    return model.export(format="engine", int8=quantized)

def export_onnx(model):
    """
    Export the model to ONNX format.
    """
    return model.export(format="onnx")

def export_tflite(model, quantized: bool = True):
    """
    Export the model to TFLite format.
    """
    return model.export(format="tflite", int8=quantized)

def run_inference(model, preprocessed_image):
    """
    Run inference from PyTorch model.
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
