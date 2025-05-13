import os
from typing import LiteralString

from yolo import (YOLO_MODEL_2C, YOLO_MODEL_3C, YOLO_MODEL_4C, YOLO_VERSION_5, YOLO_VERSION_11, YOLO_DATASET_TO_PROCESS,
                  YOLO_DATASET_PROCESSED, YOLO_DATASET_ORGANIZED, YOLO_DATASET_RESIZED, YOLO_DATASET_ORIGINAL,
                  YOLO_DATASET, YOLO_DATASET_GENERAL, YOLO_DIR, YOLO_RUNS, YOLO_WEIGHTS, BEST_PT, YOLO_DATASET_LABELED,
                  YOLO_DATASET_AUGMENTED)

# Check validity of model name
def check_model_name(model_name: str) -> None:
    if model_name not in [YOLO_MODEL_2C, YOLO_MODEL_3C, YOLO_MODEL_4C]:
        raise ValueError(f"Invalid model name: {model_name}. Must be '{YOLO_MODEL_2C}', '{YOLO_MODEL_3C}' or '{YOLO_MODEL_4C}'.")

# Check validity of model version
def check_model_version(model_version: str) -> None:
    if model_version not in [YOLO_VERSION_5, YOLO_VERSION_11]:
        raise ValueError(f"Invalid model version: {model_version}. Must be '{YOLO_VERSION_5}' or '{YOLO_VERSION_11}'.")

# Check validity of dataset status
def check_dataset_status(dataset_status: str) -> None:
    if dataset_status not in [YOLO_DATASET_TO_PROCESS, YOLO_DATASET_PROCESSED]:
        raise ValueError(f"Invalid dataset status: {dataset_status}. Must be '{YOLO_DATASET_TO_PROCESS}' or '{YOLO_DATASET_PROCESSED}'.")

# Check validity of dataset name
def check_dataset_name(dataset_name:str, model_name:str|None)-> None:
    # Check if the dataset name is split by model name
    if model_name is not None:
        if dataset_name in [YOLO_DATASET_ORIGINAL, YOLO_DATASET_RESIZED]:
            raise ValueError(f"Invalid dataset path. The dataset name '{dataset_name}' should not be used with model name '{model_name}'.")

    # Check if the dataset name is split by model name
    elif dataset_name not in [YOLO_DATASET_ORIGINAL, YOLO_DATASET_RESIZED]:
        raise ValueError(f"Invalid dataset path. The dataset name '{dataset_name}' should not be used without a model name.")

    # Check validity of dataset name
    if dataset_name not in [YOLO_DATASET_ORIGINAL, YOLO_DATASET_RESIZED, YOLO_DATASET_LABELED, YOLO_DATASET_AUGMENTED,
                                       YOLO_DATASET_ORGANIZED]:
        raise ValueError(f"Invalid dataset name: {dataset_name}. Must be one of the defined dataset folders.")

# Get dataset model directory path
def get_dataset_model_dir_path(dataset_name: str, dataset_status: str, model_name: str|None) -> LiteralString | str | bytes:
    # Check dataset status
    check_dataset_status(dataset_status)

    # Check dataset name
    check_dataset_name(dataset_name, model_name)

    # Check if the dataset is split by model name
    if model_name is not None:
        return os.path.join(YOLO_DATASET, model_name, dataset_name, dataset_status)

    return os.path.join(YOLO_DATASET, YOLO_DATASET_GENERAL, dataset_name, dataset_status)

# Get model weights path
def get_model_weight_dir_path(model_name: str, model_version: str) -> LiteralString | str | bytes:
    # Check model name
    check_model_name(model_name)

    # Check model version
    check_model_version(model_version)

    return os.path.join(YOLO_DIR, model_version, YOLO_RUNS, model_name, YOLO_WEIGHTS)

# Get model best PyTorch path
def get_model_best_pt_path(model_name: str, model_version: str) -> LiteralString | str | bytes:
    # Get model weight path
    model_weight_path = get_model_weight_dir_path(model_name, model_version)

    return os.path.join(model_weight_path, BEST_PT)