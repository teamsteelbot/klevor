import os
import time
from typing import LiteralString

from yolo import (YOLO_DATASET, YOLO_DATASET_GENERAL, YOLO_DIR, YOLO_RUNS, YOLO_WEIGHTS, BEST_PT,
                  YOLO_ZIP, YOLO_COLAB, YOLO_DATA, YOLO_NOTEBOOKS, YOLO_LOCAL, YOLO_RUNS_OLD,
                  YOLO_TF_RECORDS, YOLO_DATASET_NOTES_JSON, YOLO_DATASET_CLASSES_TXT, YOLO_HAILO,
                  YOLO_SUITE, BEST_ONNX, YOLO_HAILO_MODEL_ZOO, YOLO_LIBS, YOLO_CALIB, check_model_name,
                  check_dataset_status, check_model_dataset_status, check_dataset_name, check_model_dataset_name,
                  check_yolo_version)

# Get the dataset model directory path
def get_dataset_model_dir_path(dataset_name: str, dataset_status: str|None, model_name: str|None) -> LiteralString | str | bytes:
    # Check the validity of the model name
    if model_name is not None:
        check_model_name(model_name)

    # Check the validity of the dataset status
    if dataset_status is not None:
        check_dataset_status(dataset_status)
        check_model_dataset_status(dataset_name, dataset_status)

    # Check the validity of the dataset name
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

# Get the YOLO version folder path
def get_yolo_version_dir_path(yolo_version: str) -> LiteralString | str | bytes:
    # Check the validity of the YOLO version
    check_yolo_version(yolo_version)

    return os.path.join(YOLO_DIR, yolo_version)

# Get the YOLO runs folder path
def get_yolo_runs_dir_path(yolo_version: str) -> LiteralString | str | bytes:
    # Get the YOLO version folder path
    yolo_version_dir = get_yolo_version_dir_path(yolo_version)

    return os.path.join(yolo_version_dir, YOLO_RUNS)

# Get the YOLO runs folder path with the new name
def get_yolo_runs_new_name_dir_path(yolo_version: str) -> LiteralString | str | bytes:
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

    # Check the validity of the model name
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
    # Check the validity of the YOLO version
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
    # Check the validity of the model name
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
    # Check the validity of the YOLO version
    check_yolo_version(yolo_version)    
    
    return os.path.join(YOLO_DIR, yolo_version, YOLO_NOTEBOOKS)

# Get the TF Record path
def get_tf_record_path(model_name: str, yolo_version: str) -> LiteralString | str | bytes:
    # Get the YOLO version folder path
    yolo_version_dir = get_yolo_version_dir_path(yolo_version)

    # Check the validity of the model name
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

# Get the Hailo Suite folder path
def get_hailo_suite_dir_path() -> LiteralString | str | bytes:
    return os.path.join(YOLO_DIR, YOLO_HAILO, YOLO_SUITE)

# Get the model Hailo Suite path
def get_model_hailo_suite_dir_path(model_name: str, yolo_version: str) -> LiteralString | str | bytes:
    # Get the Hailo Suite folder path
    hailo_suite_dir = get_hailo_suite_dir_path()

    # Check the validity of the model name
    check_model_name(model_name)

    # Check the validity of the YOLO version
    check_yolo_version(yolo_version)

    return os.path.join(hailo_suite_dir, yolo_version, model_name)

# Get the model Hailo Suite file path
def get_model_hailo_suite_file_path(model_name: str, yolo_version: str, filename) -> LiteralString | str | bytes:
    # Get the model Hailo Suite path
    model_hailo_suite_dir = get_model_hailo_suite_dir_path(model_name, yolo_version)

    return os.path.join(model_hailo_suite_dir, filename)

# Get the Hailo Suite parsed filename
def get_model_parsed_har_file_name(model_name: str) -> LiteralString | str | bytes:
    return f'{model_name}_parsed.har'

# Get the Hailo Suite optimized filename
def get_model_optimized_har_file_name(model_name: str) -> LiteralString | str | bytes:
    return f'{model_name}_optimized.har'

# Get the Hailo Suite compiled filename
def get_model_compiled_hef_file_name(model_name: str) -> LiteralString | str | bytes:
    return f'{model_name}_compiled.hef'

"""
# Get the Hailo Suite parsed filename
def get_model_parsed_har_file_name(weights_name: str) -> LiteralString | str | bytes:
    return f'{weights_name}_parsed.har'

# Get the Hailo Suite optimized filename
def get_model_optimized_har_file_name(weights_name: str) -> LiteralString | str | bytes:
    return f'{weights_name}_optimized.har'

# Get the Hailo Suite compiled filename
def get_model_compiled_hef_file_name(weights_name: str) -> LiteralString | str | bytes:
    return f'{weights_name}_compiled.hef'
"""

# Get the Hailo Suite calibration set folder
def get_hailo_suite_calib_dir_path() -> LiteralString | str | bytes:
    # Get the model Hailo Suite path
    model_hailo_suite_dir = get_hailo_suite_dir_path()

    return os.path.join(model_hailo_suite_dir, YOLO_CALIB)

# Get the Hailo Suite calibration set file path
def get_hailo_suite_calib_file_path() -> LiteralString | str | bytes:
    # Get the Hailo Suite calibration set folder path
    hailo_suite_calib_dir = get_hailo_suite_calib_dir_path()

    return os.path.join(hailo_suite_calib_dir, YOLO_CALIB + '.npy')

# Get the Hailo Model Zoo path
def get_hailo_model_zoo_dir_path() -> LiteralString | str | bytes:
    return os.path.join(YOLO_DIR, YOLO_HAILO, YOLO_SUITE, YOLO_LIBS, YOLO_HAILO_MODEL_ZOO)