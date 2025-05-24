import os
from time import time
from typing import LiteralString

from yolo import (YOLO_DATASET, YOLO_DATASET_GENERAL, YOLO_DIR, YOLO_RUNS, YOLO_WEIGHTS, BEST_PT,
                  YOLO_ZIP, YOLO_COLAB, YOLO_DATA, YOLO_NOTEBOOKS, YOLO_LOCAL, YOLO_RUNS_OLD,
                  YOLO_TF_RECORDS, YOLO_DATASET_NOTES_JSON, YOLO_DATASET_CLASSES_TXT, YOLO_HAILO,
                  YOLO_HAILO_SUITE, BEST_ONNX, YOLO_HAILO_MODEL_ZOO, YOLO_HAILO_LIBS, YOLO_HAILO_CALIB,
                  check_model_name,
                  check_dataset_status, check_model_dataset_status, check_dataset_name, check_model_dataset_name,
                  check_yolo_version, LOGS_DIR, YOLO_HAILO_LABELS)

def get_dataset_model_dir_path(dataset_name: str, dataset_status: str|None, model_name: str|None) -> LiteralString | str | bytes:
    """
    Get the dataset model directory path.
    """
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

def get_yolo_version_dir_path(yolo_version: str) -> LiteralString | str | bytes:
    """
    Get the YOLO version folder path.
    """
    # Check the validity of the YOLO version
    check_yolo_version(yolo_version)

    return os.path.join(YOLO_DIR, yolo_version)

def get_yolo_runs_dir_path(yolo_version: str) -> LiteralString | str | bytes:
    """
    Get the YOLO runs folder path.
    """
    # Get the YOLO version folder path
    yolo_version_dir = get_yolo_version_dir_path(yolo_version)

    return os.path.join(yolo_version_dir, YOLO_RUNS)

def get_yolo_runs_new_name_dir_path(yolo_version: str) -> LiteralString | str | bytes:
    """
    Get the YOLO runs folder path with the new name.
    """
    # Get the YOLO version folder path
    yolo_version_dir = get_yolo_version_dir_path(yolo_version)

    # Get the current Unix timestamp
    unix_timestamp = int(time())

    return os.path.join(yolo_version_dir, f'{YOLO_RUNS}_{unix_timestamp}')

def get_yolo_old_runs_dir_path(yolo_version: str) -> LiteralString | str | bytes:
    """
    Get the YOLO old runs folder path.
    """
    # Get the YOLO version folder path
    yolo_version_dir = get_yolo_version_dir_path(yolo_version)

    return os.path.join(yolo_version_dir, YOLO_RUNS_OLD)

def get_model_runs_dir_path(model_name: str, yolo_version: str) -> LiteralString | str | bytes:
    """
    Get the model runs path.
    """
    # Get the YOLO runs folder path
    yolo_runs_dir = get_yolo_runs_dir_path(yolo_version)

    # Check the validity of the model name
    check_model_name(model_name)

    return os.path.join(yolo_runs_dir, model_name)

def get_model_weight_dir_path(model_name: str, yolo_version: str) -> LiteralString | str | bytes:
    """
    Get the model weights path.
    """
    # Get the model runs path
    model_runs_path = get_model_runs_dir_path(model_name, yolo_version)

    return os.path.join(model_runs_path, YOLO_WEIGHTS)

def get_model_best_pt_path(model_name: str, yolo_version: str) -> LiteralString | str | bytes:
    """
    Get the model best PyTorch path.
    """
    # Get the model weight path
    model_weight_path = get_model_weight_dir_path(model_name, yolo_version)

    return os.path.join(model_weight_path, BEST_PT)

def get_model_best_onnx_path(model_name: str, yolo_version: str) -> LiteralString | str | bytes:
    """
    Get  the model best ONNX path.
    """
    # Get the model weight path
    model_weight_path = get_model_weight_dir_path(model_name, yolo_version)

    return os.path.join(model_weight_path, BEST_ONNX)

def get_yolo_zip_dir_path(yolo_version: str) -> LiteralString | str | bytes:
    """
    Get the YOLO zip folder path.
    """
    # Check the validity of the YOLO version
    check_yolo_version(yolo_version)

    return os.path.join(YOLO_DIR, yolo_version, YOLO_ZIP)

def get_yolo_data_dir_path() -> LiteralString | str | bytes:
    """
    Get the YOLO data folder path.
    """
    return os.path.join(YOLO_DIR, YOLO_DATA)

def get_yolo_colab_data_dir_path() -> LiteralString | str | bytes:
    """
    Get the YOLO colab data folder path.
    """
    # Get the model data folder path
    yolo_data_dir = get_yolo_data_dir_path()

    return os.path.join(yolo_data_dir, YOLO_COLAB)

def get_yolo_local_data_dir_path() -> LiteralString | str | bytes:
    """
    Get the YOLO local data folder path.
    """
    # Get the model data folder path
    yolo_data_dir = get_yolo_data_dir_path()

    return os.path.join(yolo_data_dir, YOLO_LOCAL)

def get_model_data_name(model_name: str) -> str:
    """
    Get the model data name.
    """
    # Check the validity of the model name
    check_model_name(model_name)

    return model_name + '.yaml'

def get_model_colab_data_path(model_name: str) -> LiteralString | str | bytes:
    """
    Get the model Colab data path.
    """
    # Get the model Colab data folder path
    yolo_colab_data_dir = get_yolo_colab_data_dir_path()

    # Get the model data name
    model_data_name = get_model_data_name(model_name)

    return os.path.join(yolo_colab_data_dir, model_data_name)

def get_model_local_data_path(model_name: str) -> LiteralString | str | bytes:
    """
    Get the model local data path.
    """
    # Get the model local data folder path
    yolo_local_data_dir = get_yolo_local_data_dir_path()

    # Get the model data name
    model_data_name = get_model_data_name(model_name)

    return os.path.join(yolo_local_data_dir, model_data_name)

def get_yolo_notebooks_dir_path(yolo_version: str) -> LiteralString | str | bytes:
    """
    Get the YOLO notebooks folder path.
    """
    # Check the validity of the YOLO version
    check_yolo_version(yolo_version)    
    
    return os.path.join(YOLO_DIR, yolo_version, YOLO_NOTEBOOKS)

def get_tf_record_path(model_name: str, yolo_version: str) -> LiteralString | str | bytes:
    """
    Get the TensorFlow Record path.
    """
    # Get the YOLO version folder path
    yolo_version_dir = get_yolo_version_dir_path(yolo_version)

    # Check the validity of the model name
    check_model_name(model_name)

    return os.path.join(yolo_version_dir, YOLO_TF_RECORDS, model_name+'.tfrecord')

def get_yolo_dataset_notes_file_path(dataset_name: str, dataset_status: str|None, model_name: str|None) -> LiteralString | str | bytes:
    """
    Get the YOLO dataset notes file path.
    """
    # Get the dataset model directory path
    dataset_model_dir_path = get_dataset_model_dir_path(dataset_name, dataset_status, model_name)

    return os.path.join(dataset_model_dir_path, YOLO_DATASET_NOTES_JSON)

def get_yolo_dataset_classes_file_path(dataset_name: str, dataset_status: str|None, model_name: str|None) -> LiteralString | str | bytes:
    """
    Get the YOLO dataset classes file path.
    """
    # Get the dataset model directory path
    dataset_model_dir_path = get_dataset_model_dir_path(dataset_name, dataset_status, model_name)

    return os.path.join(dataset_model_dir_path, YOLO_DATASET_CLASSES_TXT)

def get_hailo_dir_path() -> LiteralString | str | bytes:
    """
    Get the Hailo folder path.
    """
    return os.path.join(YOLO_DIR, YOLO_HAILO)

def get_hailo_suite_dir_path() -> LiteralString | str | bytes:
    """
    Get the Hailo Suite folder path.
    """
    # Get the Hailo folder path
    hailo_dir = get_hailo_dir_path()

    return os.path.join(hailo_dir, YOLO_HAILO_SUITE)

def get_model_hailo_suite_dir_path(model_name: str, yolo_version: str) -> LiteralString | str | bytes:
    """
    Get the model Hailo Suite path.
    """
    # Get the Hailo Suite folder path
    hailo_suite_dir = get_hailo_suite_dir_path()

    # Check the validity of the model name
    check_model_name(model_name)

    # Check the validity of the YOLO version
    check_yolo_version(yolo_version)

    return os.path.join(hailo_suite_dir, yolo_version, model_name)

def get_model_hailo_suite_file_path(model_name: str, yolo_version: str, filename) -> LiteralString | str | bytes:
    """
    Get the model Hailo Suite file path.
    """
    # Get the model Hailo Suite path
    model_hailo_suite_dir = get_model_hailo_suite_dir_path(model_name, yolo_version)

    return os.path.join(model_hailo_suite_dir, filename)

def get_model_hailo_suite_parsed_har_file_name(model_name: str) -> LiteralString | str | bytes:
    """
    Get the Hailo Suite parsed filename.
    """
    return f'{model_name}_parsed.har'

def get_model_hailo_suite_optimized_har_file_name(model_name: str) -> LiteralString | str | bytes:
    """
    Get the Hailo Suite optimized filename.
    """
    return f'{model_name}_optimized.har'

def get_model_hailo_suite_compiled_hef_file_name(model_name: str) -> LiteralString | str | bytes:
    """
    Get the Hailo Suite compiled filename.
    """
    return f'{model_name}_compiled.hef'

def get_model_hailo_suite_parsed_har_file_path(model_name: str, yolo_version: str) -> LiteralString | str | bytes:
    """
    Get the model Hailo Suite parsed file path.
    """
    # Get the model Hailo Suite path
    model_hailo_suite_dir = get_model_hailo_suite_dir_path(model_name, yolo_version)

    # Get the Hailo Suite parsed filename
    model_hailo_suite_parsed_har_file_name = get_model_hailo_suite_parsed_har_file_name(model_name)

    return os.path.join(model_hailo_suite_dir, model_hailo_suite_parsed_har_file_name)

def get_model_hailo_suite_optimized_har_file_path(model_name: str, yolo_version: str) -> LiteralString | str | bytes:
    """
    Get the model Hailo Suite optimized file path.
    """
    # Get the model Hailo Suite path
    model_hailo_suite_dir = get_model_hailo_suite_dir_path(model_name, yolo_version)

    # Get the Hailo Suite optimized filename
    model_hailo_suite_optimized_har_file_name = get_model_hailo_suite_optimized_har_file_name(model_name)

    return os.path.join(model_hailo_suite_dir, model_hailo_suite_optimized_har_file_name)

def get_model_hailo_suite_compiled_hef_file_path(model_name: str, yolo_version: str) -> LiteralString | str | bytes:
    """
    Get the model Hailo Suite compiled file path.
    """
    # Get the model Hailo Suite path
    model_hailo_suite_dir = get_model_hailo_suite_dir_path(model_name, yolo_version)

    # Get the Hailo Suite compiled filename
    model_hailo_suite_compiled_hef_file_name = get_model_hailo_suite_compiled_hef_file_name(model_name)

    return os.path.join(model_hailo_suite_dir, model_hailo_suite_compiled_hef_file_name)

def get_model_weights_parsed_har_file_path(model_name: str, yolo_version: str) -> LiteralString | str | bytes:
    """
    Get the model weights parsed file path.
    """
    # Get the model weights directory path
    model_weights_dir = get_model_weight_dir_path(model_name, yolo_version)

    return os.path.join(model_weights_dir, 'parsed.har')

def get_model_weights_optimized_har_file_path(model_name: str, yolo_version: str) -> LiteralString | str | bytes:
    """
    Get the model weights optimized file path.
    """
    # Get the model weights directory path
    model_weights_dir = get_model_weight_dir_path(model_name, yolo_version)

    return os.path.join(model_weights_dir, 'optimized.har')

def get_model_weights_compiled_hef_file_path(model_name: str, yolo_version: str) -> LiteralString | str | bytes:
    """
    Get the model weights compiled file path.
    """
    # Get the model weights directory path
    model_weights_dir = get_model_weight_dir_path(model_name, yolo_version)

    return os.path.join(model_weights_dir, 'compiled.hef')

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

def get_hailo_suite_calib_dir_path() -> LiteralString | str | bytes:
    """
    Get the Hailo Suite calibration set folder.
    """
    # Get the model Hailo Suite path
    model_hailo_suite_dir = get_hailo_suite_dir_path()

    return os.path.join(model_hailo_suite_dir, YOLO_HAILO_CALIB)

def get_hailo_suite_calib_file_path() -> LiteralString | str | bytes:
    """
    Get the Hailo Suite calibration set file path.
    """
    # Get the Hailo Suite calibration set folder path
    hailo_suite_calib_dir = get_hailo_suite_calib_dir_path()

    return os.path.join(hailo_suite_calib_dir, YOLO_HAILO_CALIB + '.npy')

def get_hailo_model_zoo_dir_path() -> LiteralString | str | bytes:
    """
    Get the Hailo Model Zoo path
    """
    return os.path.join(YOLO_DIR, YOLO_HAILO, YOLO_HAILO_SUITE, YOLO_HAILO_LIBS, YOLO_HAILO_MODEL_ZOO)

def get_log_file_path() -> LiteralString | str | bytes:
    """
    Get the log file path.
    """
    # Get the UNIX timestamp
    unix_timestamp = int(time())

    return os.path.join(LOGS_DIR, f'{unix_timestamp}.txt')

def get_hailo_labels_dir_path() -> LiteralString | str | bytes:
    """
    Get the Hailo labels folder path.
    """
    # Get the Hailo folder path
    hailo_dir = get_hailo_dir_path()

    return os.path.join(hailo_dir, YOLO_HAILO_LABELS)

def get_hailo_labels_file_path(model_name: str) -> LiteralString | str | bytes:
    """
    Get the Hailo labels file path.
    """
    # Check the validity of the model name
    check_model_name(model_name)

    # Get the Hailo labels folder path
    hailo_labels_dir = get_hailo_labels_dir_path()

    return os.path.join(hailo_labels_dir, model_name+'.txt')