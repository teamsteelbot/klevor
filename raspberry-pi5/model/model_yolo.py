import os
import time
from typing import LiteralString
from pathlib import Path

import torch
from ultralytics import YOLO
from yolo import (YOLO_DATASET, YOLO_TO_PROCESS, YOLO_PROCESSED,
                  YOLO_DATASET_ORIGINAL, YOLO_DATASET_RESIZED, YOLO_DATASET_LABELED, YOLO_DATASET_AUGMENTED,
                  YOLO_DATASET_ORGANIZED, SPACER, YOLO_MODEL_2C, YOLO_MODEL_4C, YOLO_VERSION_5, YOLO_VERSION_11,
                  YOLO_RUNS, YOLO_NAME, YOLO_WEIGHTS, BEST_PT, YOLO_DIR, )

# Load YOLO PyTorch model
def load(model: str, task='detect'):
    # Check if the model has a parent directory
    if Path(model).parent != Path('.'):
        # Verify the model file exists
        if not os.path.exists(model):
            raise FileNotFoundError(f"Model file not found: {model}")

    # Load the model
    model = YOLO(model, task=task, verbose=True)
    return model


# Get YOLO PyTorch model class names
def get_class_names(model):
    # Detected PyTorch model class names
    print(f'Classes: {model.names}')

    return model.names


# Export the model to TensorRT format
def export_tensor_rt(model, quantized: bool = True):
    return model.export(format="engine", int8=quantized)


# Export the model to ONNX format
def export_onnx(model):
    return model.export(format="onnx")


# Export the model to TFLite format
def export_tflite(model, quantized: bool = True):
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

# Check validity of model name
def check_model_name(model_name: str) -> None:
    if model_name not in [YOLO_MODEL_2C, YOLO_MODEL_4C]:
        raise ValueError(f"Invalid model name: {model_name}. Must be '{YOLO_MODEL_2C}' or '{YOLO_MODEL_4C}'.")

# Check validity of model version
def check_model_version(model_version: str) -> None:
    if model_version not in [YOLO_VERSION_5, YOLO_VERSION_11]:
        raise ValueError(f"Invalid model version: {model_version}. Must be '{YOLO_VERSION_5}' or '{YOLO_VERSION_11}'.")

# Check validity of dataset status
def check_dataset_status(dataset_status: str) -> None:
    if dataset_status not in [YOLO_TO_PROCESS, YOLO_PROCESSED]:
        raise ValueError(f"Invalid dataset status: {dataset_status}. Must be '{YOLO_TO_PROCESS}' or '{YOLO_PROCESSED}'.")

# Check validity of dataset name
def check_dataset_name(dataset_name:str, model_name:str|None)-> None:
    # Check if the dataset name is split by model name
    if model_name is not None:
        if dataset_name in [YOLO_DATASET_ORIGINAL, YOLO_DATASET_RESIZED]:
            raise ValueError(f"Invalid dataset path. The dataset name '{dataset_name}' should not be used with model name '{model_name}'.")

    # Check if the dataset name is split by model name
    elif dataset_name in [YOLO_DATASET_ORIGINAL, YOLO_DATASET_RESIZED]:
        raise ValueError(f"Invalid dataset path. The dataset name '{dataset_name}' should not be used without a model name.")

    # Check validity of dataset name
    if dataset_name not in [YOLO_DATASET_ORIGINAL, YOLO_DATASET_RESIZED, YOLO_DATASET_LABELED, YOLO_DATASET_AUGMENTED,
                                       YOLO_DATASET_ORGANIZED]:
        raise ValueError(f"Invalid dataset name: {dataset_name}. Must be one of the defined dataset folders.")

# Get dataset model name
def get_dataset_model_name(dataset_name: str, model_name: str|None) -> str:
    # Check model name
    check_model_name(model_name)

    # Check dataset name
    check_dataset_name(dataset_name, model_name)

    # Get dataset model name
    if model_name is not None:
        return f'{dataset_name}{SPACER}{model_name}'
    return dataset_name

# Get dataset path
def get_dataset_images_path(dataset_name: str, dataset_status: str, model_name: str|None) -> LiteralString | str | bytes:
    # Get dataset model name
    dataset_name = get_dataset_model_name(dataset_name, model_name)

    # Check dataset status
    check_dataset_status(dataset_status)

    # Get dataset path
    return os.path.join(YOLO_DATASET, dataset_name, dataset_status)

# Get YOLO model name
def get_model_name(model_name: str) -> str:
    # Check model name
    check_model_name(model_name)

    return YOLO_NAME + SPACER + model_name

# Get model best PyTorch path
def get_model_best_pt_path(model_name: str, model_version: str) -> LiteralString | str | bytes:
    # Get model weight path
    model_weight_path = get_model_weight_path(model_name, model_version)

    return os.path.join(model_weight_path, BEST_PT)

# Get model weights path
def get_model_weight_path(model_name: str, model_version: str) -> LiteralString | str | bytes:
    # Check model name
    check_model_name(model_name)

    # Check model version
    check_model_version(model_version)

    # Get YOLO model name
    model_name = get_model_name(model_name)

    return os.path.join(YOLO_DIR, model_version, YOLO_RUNS, model_name, YOLO_WEIGHTS)