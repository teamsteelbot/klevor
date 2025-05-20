import argparse
import os
import shutil

from args import parse_args_as_dict, get_attribute_from_args
from yolo import ARGS_YOLO_INPUT_MODEL, ARGS_YOLO_VERSION, YOLO_DATASET_TRAINING
from yolo.args import add_yolo_input_model_argument, add_yolo_version_argument
from yolo.files import (get_model_parsed_har_file_name, get_model_weight_dir_path, get_model_hailo_suite_dir_path,
                        get_model_optimized_har_file_name, get_model_compiled_hef_file_name, get_hailo_model_zoo_dir_path,
                        get_hailo_suite_dir_path)


# Copy files from the Hailo Model Zoo folder and remove the training folder from the model Hailo Suite folder
def after_compilation(model_name, hailo_model_zoo_dir, hailo_suite_dir, model_weights_dir):
    # Get the parsed, optimized, and compiled model names
    parsed_model_name = get_model_parsed_har_file_name(model_name)
    optimized_model_name = get_model_optimized_har_file_name(model_name)
    compiled_model_name = get_model_compiled_hef_file_name(model_name)

    # Get the training images folder from model Hailo Suite folder
    model_hailo_suite_training_dir = os.path.join(hailo_suite_dir, YOLO_DATASET_TRAINING)
    
    # Remove the training images folder from the model Hailo Suite folder
    if os.path.exists(model_hailo_suite_training_dir):
        shutil.rmtree(model_hailo_suite_training_dir)
        print(f'Removed {YOLO_DATASET_TRAINING} folder from {hailo_suite_dir} folder')
    else:
        print(f'{YOLO_DATASET_TRAINING} folder does not exist in {hailo_suite_dir}')

    # Copy the generated '.har' and '.hef' files from the Hailo Model Zoo folder
    for file in [parsed_model_name, optimized_model_name, compiled_model_name]:
        src = os.path.join(hailo_model_zoo_dir, file)
        dst = os.path.join(model_weights_dir, ' '.join(file.split('_')[1:]))
        if os.path.exists(src):
            shutil.copy(src, dst)
            print(f'Copied {src} to {dst}')
        else:
            print(f'{src} does not exist')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Script to copy the generated '.har' and '.hef' files from the Hailo Suite folder")
    add_yolo_input_model_argument(parser)
    add_yolo_version_argument(parser)
    args = parse_args_as_dict(parser)

    # Get the YOLO input model
    arg_yolo_input_model = get_attribute_from_args(args, ARGS_YOLO_INPUT_MODEL)

    # Get the YOLO version
    arg_yolo_version = get_attribute_from_args(args, ARGS_YOLO_VERSION)

    # Get the Hailo Model Zoo folder
    hailo_model_zoo_dir = get_hailo_model_zoo_dir_path()

    # Get the Hailo Suite path
    hailo_suite_dir = get_hailo_suite_dir_path()
    
    # Get the weights folder
    model_weights_dir = get_model_weight_dir_path(arg_yolo_input_model, arg_yolo_version)

    # Copy the files from the Hailo Model Zoo folder
    after_compilation(arg_yolo_input_model, hailo_model_zoo_dir, hailo_suite_dir, model_weights_dir)