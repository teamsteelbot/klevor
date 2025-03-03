import os
import time
import torch
from ultralytics import YOLO

# Load YOLO PyTorch model
def load(model_path: str, task='detect'):
    # Verify the model file exists
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")

    # Load the model
    model= YOLO(model_path, task=task, verbose=True)
    return model

# Get YOLO PyTorch model class names
def get_class_names(model):
    # Detected PyTorch model class names
    print(f'Classes: {model.names}')

    return model.names

# Export the model to TensorRT format
def export_tensor_rt(model, quantized:bool=True):
    return model.export(format="engine", int8=quantized)

# Export the model to ONNX format
def export_onnx(model):
    return model.export(format="onnx")

# Export the model to TFLite format
def export_tflite(model, quantized:bool=True):
    return model.export(format="tflite", int8=quantized)

# Run inference from PyTorch model
def run_inference(model, preprocessed_image):
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