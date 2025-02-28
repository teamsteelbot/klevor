import os
import time
import onnx
import onnxruntime as ort
from yolo.constants import ONNX_METADATA_CLASS_NAMES_KEY
from ultralytics import YOLO
import torch

# Load PyTorch model
def load_pt_model(model_path: str):
    # Verify the model file exists
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")

    # Load the model
    model = YOLO(model_path)
    model.eval()
    return model

# Get PyTorch model class names
def get_pt_model_class_names(model):
    # Detected PyTorch model class names
    print(f'Classes: {model.names}')

    return model.names

# Load ONNX model
def load_onnx_model(model_path: str):
    # Verify the model file exists
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")

    # Load the ONNX model
    model = onnx.load_model(model_path)
    session = ort.InferenceSession(model_path)

    return model, session

# Get ONNX model class names
def get_onnx_model_class_names(model):
    for p in model.metadata_props:
        if p.key == ONNX_METADATA_CLASS_NAMES_KEY:
            # Detected ONNX model class names
            print(f'Classes: {p.value}')

            return p.value