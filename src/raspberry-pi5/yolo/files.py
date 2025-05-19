import os
import time
from typing import LiteralString

from yolo import (YOLO_MODEL_GR, YOLO_MODEL_GMR, YOLO_MODEL_BGOR, YOLO_VERSION_5, YOLO_VERSION_11,
                  YOLO_DATASET_TO_PROCESS,
                  YOLO_DATASET_PROCESSED, YOLO_DATASET_ORGANIZED, YOLO_DATASET_RESIZED, YOLO_DATASET_ORIGINAL,
                  YOLO_DATASET, YOLO_DATASET_GENERAL, YOLO_DIR, YOLO_RUNS, YOLO_WEIGHTS, BEST_PT, YOLO_DATASET_LABELED,
                  YOLO_DATASET_AUGMENTED, YOLO_ZIP, YOLO_COLAB, YOLO_DATA, YOLO_NOTEBOOKS, YOLO_LOCAL, YOLO_RUNS_OLD,
                  YOLO_TF_RECORDS, YOLO_DATASET_NOTES_JSON, YOLO_DATASET_CLASSES_TXT, YOLO_MODEL_M, YOLO_HAILO,
                  YOLO_SUITE, BEST_ONNX, YOLO_HAILO_MODEL_ZOO, YOLO_LIBS)

# Check validity of model name
def check_model_name(model_name: str) -> None:
    if model_name not in [YOLO_MODEL_M, YOLO_MODEL_GR, YOLO_MODEL_GMR, YOLO_MODEL_BGOR]:
        raise ValueError(f"Invalid model name: {model_name}. Must be '{YOLO_MODEL_M}', '{YOLO_MODEL_GR}', '{YOLO_MODEL_GMR}' or '{YOLO_MODEL_BGOR}'.")

# Check validity of yolo version
def check_yolo_version(yolo_version: str) -> None:
    if yolo_version not in [YOLO_VERSION_5, YOLO_VERSION_11]:
        raise ValueError(f"Invalid yolo version: {yolo_version}. Must be '{YOLO_VERSION_5}' or '{YOLO_VERSION_11}'.")

# Check validity of dataset status
def check_dataset_status(dataset_status: str|None) -> None:
    if dataset_status is not None:
        if dataset_status not in [YOLO_DATASET_TO_PROCESS, YOLO_DATASET_PROCESSED]:
            raise ValueError(f"Invalid dataset status: {dataset_status}. Must be '{YOLO_DATASET_TO_PROCESS}' or '{YOLO_DATASET_PROCESSED}'.")

# Check validity of model dataset status
def check_model_dataset_status(dataset_name: str, dataset_status: str|None) -> None:
    # Check if the dataset name is split by dataset status
    if dataset_status is not None:
        if dataset_name in [YOLO_DATASET_AUGMENTED, YOLO_DATASET_ORGANIZED]:
            raise ValueError(f"Invalid dataset path. The dataset name '{dataset_name}' should not be used with dataset status '{dataset_status}'.")

# Check validity of dataset name
def check_dataset_name(dataset_name: str) -> None:
    # Check validity of dataset name
    if dataset_name not in [YOLO_DATASET_ORIGINAL, YOLO_DATASET_RESIZED, YOLO_DATASET_LABELED, YOLO_DATASET_AUGMENTED,
                            YOLO_DATASET_ORGANIZED]:
        raise ValueError(f"Invalid dataset name: {dataset_name}. Must be one of the defined dataset folders.")

# Check validity of the model dataset name
def check_model_dataset_name(dataset_name:str, model_name:str|None)-> None:
    # Check if the dataset name is split by model name
    if model_name is not None:
        if dataset_name in [YOLO_DATASET_ORIGINAL, YOLO_DATASET_RESIZED]:
            raise ValueError(f"Invalid dataset path. The dataset name '{dataset_name}' should not be used with model name '{model_name}'.")

    # Check if the dataset name is split by model name
    elif dataset_name not in [YOLO_DATASET_ORIGINAL, YOLO_DATASET_RESIZED]:
        raise ValueError(f"Invalid dataset path. The dataset name '{dataset_name}' should not be used without a model name.")

# Get the dataset model directory path
def get_dataset_model_dir_path(dataset_name: str, dataset_status: str|None, model_name: str|None) -> LiteralString | str | bytes:
    # Check model name
    if model_name is not None:
        check_model_name(model_name)

    # Check dataset status
    if dataset_status is not None:
        check_dataset_status(dataset_status)
        check_model_dataset_status(dataset_name, dataset_status)

    # Check dataset name
    check_dataset_name(dataset_name)
    check_model_dataset_name(dataset_name, model_name)

    # Check if the dataset is split by model name
    if dataset_status is not None and model_name is not None:
        return os.path.join(YOLO_DATASET, model_name, dataset_name, dataset_status)

    if dataset_status is not None:
        return os.path.join(YOLO_DATASET, YOLO_DATASET_GENERAL, dataset_name, dataset_status)

    if model_name is not None:
        return os.path.join(YOLO_DATASET, model_name, dataset_name)

    return os.path.join(YOLO_DATASET, YOLO_DATASET_GENERAL, dataset_name)

# Get the Hailo Suite folder path
def get_hailo_suite_dir_path() -> LiteralString | str | bytes:
    return os.path.join(YOLO_DIR, YOLO_HAILO, YOLO_SUITE)

# Get the model Hailo Suite path
def get_model_hailo_suite_path(model_name: str, yolo_version: str) -> LiteralString | str | bytes:
    # Get the Hailo Suite folder path
    hailo_suite_dir = get_hailo_suite_dir_path()

    # Check model name
    check_model_name(model_name)

    # Check YOLO version
    check_yolo_version(yolo_version)

    return os.path.join(hailo_suite_dir, yolo_version, model_name)

# Get the YOLO version folder path
def get_yolo_version_dir_path(yolo_version: str) -> LiteralString | str | bytes:
    # Check yolo version
    check_yolo_version(yolo_version)

    return os.path.join(YOLO_DIR, yolo_version)

# Get the YOLO runs folder path
def get_yolo_runs_dir_path(yolo_version: str) -> LiteralString | str | bytes:
    # Get the YOLO version folder path
    yolo_version_dir = get_yolo_version_dir_path(yolo_version)

    return os.path.join(yolo_version_dir, YOLO_RUNS)

# Get the YOLO runs folder path with the new name
def get_yolo_runs_dir_new_name_path(yolo_version: str) -> LiteralString | str | bytes:
    # Get the YOLO version folder path
    yolo_version_dir = get_yolo_version_dir_path(yolo_version)

    # Get the current Unix timestamp
    current_unix_timestamp = int(time.time())

    return os.path.join(yolo_version_dir, f'{YOLO_RUNS}_{current_unix_timestamp}')

# Get the YOLO old runs folder path
def get_yolo_old_runs_dir_path(yolo_version: str) -> LiteralString | str | bytes:
    # Get the YOLO version folder path
    yolo_version_dir = get_yolo_version_dir_path(yolo_version)

    return os.path.join(yolo_version_dir, YOLO_RUNS_OLD)

# Get the model runs path
def get_model_runs_dir_path(model_name: str, yolo_version: str) -> LiteralString | str | bytes:
    # Get the YOLO runs folder path
    yolo_runs_dir = get_yolo_runs_dir_path(yolo_version)

    # Check model name
    check_model_name(model_name)

    return os.path.join(yolo_runs_dir, model_name)

# Get the model weights path
def get_model_weight_dir_path(model_name: str, yolo_version: str) -> LiteralString | str | bytes:
    # Get the model runs path
    model_runs_path = get_model_runs_dir_path(model_name, yolo_version)

    return os.path.join(model_runs_path, YOLO_WEIGHTS)

# Get the model best PyTorch path
def get_model_best_pt_path(model_name: str, yolo_version: str) -> LiteralString | str | bytes:
    # Get the model weight path
    model_weight_path = get_model_weight_dir_path(model_name, yolo_version)

    return os.path.join(model_weight_path, BEST_PT)

# Get  the model best ONNX path
def get_model_best_onnx_path(model_name: str, yolo_version: str) -> LiteralString | str | bytes:
    # Get the model weight path
    model_weight_path = get_model_weight_dir_path(model_name, yolo_version)

    return os.path.join(model_weight_path, BEST_ONNX)

# Get the YOLO zip folder path
def get_yolo_zip_dir_path(yolo_version: str) -> LiteralString | str | bytes:
    # Check yolo version
    check_yolo_version(yolo_version)

    return os.path.join(YOLO_DIR, yolo_version, YOLO_ZIP)

# Get the YOLO data folder path
def get_yolo_data_dir_path() -> LiteralString | str | bytes:
    return os.path.join(YOLO_DIR, YOLO_DATA)

# Get the YOLO colab data folder path
def get_yolo_colab_data_dir_path() -> LiteralString | str | bytes:
    # Get the model data folder path
    yolo_data_dir = get_yolo_data_dir_path()

    return os.path.join(yolo_data_dir, YOLO_COLAB)

# Get the YOLO local data folder path
def get_yolo_local_data_dir_path() -> LiteralString | str | bytes:
    # Get the model data folder path
    yolo_data_dir = get_yolo_data_dir_path()

    return os.path.join(yolo_data_dir, YOLO_LOCAL)

# Get the model data name
def get_model_data_name(model_name: str) -> str:
    # Check model name
    check_model_name(model_name)

    return model_name + '.yaml'


# Get the model Colab data path
def get_model_colab_data_path(model_name: str) -> LiteralString | str | bytes:
    # Get the model Colab data folder path
    yolo_colab_data_dir = get_yolo_colab_data_dir_path()

    # Get the model data name
    model_data_name = get_model_data_name(model_name)

    return os.path.join(yolo_colab_data_dir, model_data_name)

# Get the model local data path
def get_model_local_data_path(model_name: str) -> LiteralString | str | bytes:
    # Get the model local data folder path
    yolo_local_data_dir = get_yolo_local_data_dir_path()

    # Get the model data name
    model_data_name = get_model_data_name(model_name)

    return os.path.join(yolo_local_data_dir, model_data_name)

# Get the YOLO notebooks folder path
def get_yolo_notebooks_dir_path(yolo_version: str) -> LiteralString | str | bytes:
    # Check yolo version
    check_yolo_version(yolo_version)    
    
    return os.path.join(YOLO_DIR, yolo_version, YOLO_NOTEBOOKS)

# Get the TF Record path
def get_tf_record_path(model_name: str, yolo_version: str) -> LiteralString | str | bytes:
    # Get the YOLO version folder path
    yolo_version_dir = get_yolo_version_dir_path(yolo_version)

    # Check model name
    check_model_name(model_name)

    return os.path.join(yolo_version_dir, YOLO_TF_RECORDS, model_name+'.tfrecord')

# Get the YOLO dataset notes file path
def get_yolo_dataset_notes_file_path(dataset_name: str, dataset_status: str|None, model_name: str|None) -> LiteralString | str | bytes:
    # Get the dataset model directory path
    dataset_model_dir_path = get_dataset_model_dir_path(dataset_name, dataset_status, model_name)

    return os.path.join(dataset_model_dir_path, YOLO_DATASET_NOTES_JSON)

# Get the YOLO dataset classes file path
def get_yolo_dataset_classes_file_path(dataset_name: str, dataset_status: str|None, model_name: str|None) -> LiteralString | str | bytes:
    # Get the dataset model directory path
    dataset_model_dir_path = get_dataset_model_dir_path(dataset_name, dataset_status, model_name)

    return os.path.join(dataset_model_dir_path, YOLO_DATASET_CLASSES_TXT)

# Get the model parsed HAR file name
def get_model_parsed_har_file_name(model_name: str) -> LiteralString | str | bytes:
    # Check model name
    check_model_name(model_name)

    return os.path.join(YOLO_HAILO, model_name, f'{model_name}_parsed.har')

# Get the model optimized HAR file path
def get_model_optimized_har_file_path(model_name: str) -> LiteralString | str | bytes:
    # Check model name
    check_model_name(model_name)

    return os.path.join(YOLO_HAILO, model_name, f'{model_name}_optimized.har')

# Get the model compiled HEF file path
def get_model_compiled_hef_file_path(model_name: str) -> LiteralString | str | bytes:
    # Check model name
    check_model_name(model_name)

    return os.path.join(YOLO_HAILO, model_name, f'{model_name}_compiled.hef')

# Get the Hailo Model Zoo path
def get_hailo_model_zoo_path() -> LiteralString | str | bytes:
    return os.path.join(YOLO_DIR, YOLO_HAILO, YOLO_SUITE, YOLO_LIBS, YOLO_HAILO_MODEL_ZOO)