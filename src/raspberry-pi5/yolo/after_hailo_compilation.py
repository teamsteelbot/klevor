import argparse
import os
import shutil

from args import parse_args_as_dict, get_attribute_from_args
from yolo import ARGS_YOLO_INPUT_MODEL, ARGS_YOLO_VERSION, YOLO_DATASET_TRAINING
from yolo.args import add_yolo_input_model_argument, add_yolo_version_argument
from yolo.files import (get_hailo_suite_dir_path, get_model_hailo_suite_optimized_har_file_path,
                        get_model_hailo_suite_parsed_har_file_path, get_model_hailo_suite_compiled_hef_file_path,
                        get_model_weights_parsed_har_file_path, get_model_weights_optimized_har_file_path,
                        get_model_weights_compiled_hef_file_path)


def after_compilation(model_name, yolo_version, hailo_suite_dir):
    """
    Copy files from the Hailo Model Zoo folder and remove the training folder from the model Hailo Suite folder.
    """
    # Get the parsed, optimized, and compiled file paths
    model_hailo_suite_parsed_file_path = get_model_hailo_suite_parsed_har_file_path(model_name, yolo_version)
    model_weights_parsed_har_file_path = get_model_weights_parsed_har_file_path(model_name, yolo_version)
    model_hailo_suite_optimized_file_path = get_model_hailo_suite_optimized_har_file_path(model_name, yolo_version)
    model_weights_optimized_har_file_path = get_model_weights_optimized_har_file_path(model_name, yolo_version)
    model_hailo_suite_compiled_file_path = get_model_hailo_suite_compiled_hef_file_path(model_name, yolo_version)
    model_weights_compiled_hef_file_path = get_model_weights_compiled_hef_file_path(model_name, yolo_version)

    # Get the training images folder from model Hailo Suite folder
    model_hailo_suite_training_dir = os.path.join(hailo_suite_dir, YOLO_DATASET_TRAINING)

    # Remove the training images folder from the model Hailo Suite folder
    if os.path.exists(model_hailo_suite_training_dir):
        shutil.rmtree(model_hailo_suite_training_dir)
        print(f'Removed {YOLO_DATASET_TRAINING} folder from {hailo_suite_dir} folder')
    else:
        print(f'{YOLO_DATASET_TRAINING} folder does not exist in {hailo_suite_dir}')

    # Copy the generated '.har' and '.hef' files from the Hailo Model Zoo folder
    model_hailo_suite_file_paths = [
        model_hailo_suite_parsed_file_path,
        model_hailo_suite_optimized_file_path,
        model_hailo_suite_compiled_file_path
    ]
    model_weights_file_paths = [
        model_weights_parsed_har_file_path,
        model_weights_optimized_har_file_path,
        model_weights_compiled_hef_file_path
    ]
    for idx, src in enumerate(model_hailo_suite_file_paths):
        # Get the model weights file path
        dst = model_weights_file_paths[idx]

        # Get the source and destination file paths
        if os.path.exists(src):
            shutil.copy(src, dst)
            print(f'Copied {src} to {dst}')
        else:
            print(f'{src} does not exist')

def main() -> None:
    """
    Main function to run the script.
    """
    parser = argparse.ArgumentParser(
        description="Script to copy the generated '.har' and '.hef' files from the Hailo Suite folder")
    add_yolo_input_model_argument(parser)
    add_yolo_version_argument(parser)
    args = parse_args_as_dict(parser)

    # Get the YOLO input model
    arg_yolo_input_model = get_attribute_from_args(args, ARGS_YOLO_INPUT_MODEL)

    # Get the YOLO version
    arg_yolo_version = get_attribute_from_args(args, ARGS_YOLO_VERSION)

    # Get the Hailo Suite path
    hailo_suite_dir = get_hailo_suite_dir_path()

    # Copy the files from the Hailo Model Zoo folder
    after_compilation(arg_yolo_input_model, arg_yolo_version, hailo_suite_dir)

if __name__ == '__main__':
    main()