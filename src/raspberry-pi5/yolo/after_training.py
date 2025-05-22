import argparse
import os
import shutil

from args import get_attribute_from_args, parse_args_as_dict
from files import move_folder_content, ensure_path_exists
from yolo import (ARGS_YOLO_INPUT_MODEL, YOLO_DATASET_ORGANIZED, YOLO_DATASET_TRAINING,
                  YOLO_DATASET_VALIDATIONS, ARGS_YOLO_VERSION, YOLO_DATASET_IMAGES)
from yolo.args import add_yolo_input_model_argument, add_yolo_version_argument
from yolo.files import (get_dataset_model_dir_path, get_hailo_suite_dir_path, get_model_best_onnx_path,
                        get_model_hailo_suite_dir_path)


# Remove the YOLO training and validation folders from the dataset, move the training folder and copy the best ONNX weights to the Hailo Suite folder
def after_training(input_dir, hailo_suite_dir, model_hailo_suite_dir, best_onnx_weights_path):
    # Move the training folder to the Hailo Suite folder
    input_training_images_path = os.path.join(input_dir, YOLO_DATASET_TRAINING, YOLO_DATASET_IMAGES)
    output_training_path = os.path.join(hailo_suite_dir, YOLO_DATASET_TRAINING)
    if os.path.exists(input_training_images_path):
        move_folder_content(input_training_images_path, output_training_path)
        print(f'Moved {YOLO_DATASET_TRAINING} folder from {input_dir} folder to {output_training_path} folder')
    else:
        print(f'{YOLO_DATASET_TRAINING} folder does not exist in {input_dir}')

    # Remove the training and validations folder
    for folder in [YOLO_DATASET_TRAINING, YOLO_DATASET_VALIDATIONS]:
        folder_path = os.path.join(input_dir, folder)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
            print(f'Removed {folder} folder from {input_dir} folder')
        else:
            print(f'{folder} folder does not exist in {input_dir}')

    # Copy the best ONNX weights to the model Hailo Suite folder
    ensure_path_exists(model_hailo_suite_dir)
    if os.path.exists(best_onnx_weights_path):
        shutil.copy(best_onnx_weights_path, model_hailo_suite_dir)
        print(f'Copied {best_onnx_weights_path} to {model_hailo_suite_dir} folder')
    else:
        print(f'{best_onnx_weights_path} does not exist')

# Main function to run the script
def main() -> None:
    parser = argparse.ArgumentParser(
        description='Script to removed the unnecessary files and prepare the dataset for Hailo')
    add_yolo_input_model_argument(parser)
    add_yolo_version_argument(parser)
    args = parse_args_as_dict(parser)

    # Get the YOLO input model
    arg_yolo_input_model = get_attribute_from_args(args, ARGS_YOLO_INPUT_MODEL)

    # Get the YOLO version
    arg_yolo_version = get_attribute_from_args(args, ARGS_YOLO_VERSION)

    # Get the dataset paths
    organized_dir = get_dataset_model_dir_path(YOLO_DATASET_ORGANIZED, None, arg_yolo_input_model)

    # Get the Hailo Suite path
    hailo_suite_dir = get_hailo_suite_dir_path()

    # Get the model Hailo Suite path
    model_hailo_suite_dir = get_model_hailo_suite_dir_path(arg_yolo_input_model, arg_yolo_version)

    # Get the best weights path
    best_onnx_weights_path = get_model_best_onnx_path(arg_yolo_input_model, arg_yolo_version)

    # Move the folders
    after_training(organized_dir, hailo_suite_dir, model_hailo_suite_dir, best_onnx_weights_path)


if __name__ == '__main__':
    main()