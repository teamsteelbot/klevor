import argparse
import os
import shutil

from args import get_attribute_from_args, parse_args_as_dict
from opencv.calibration_set import preprocess_images_to_npy
from yolo import (ARGS_YOLO_INPUT_MODEL, YOLO_DATASET_ORGANIZED, YOLO_DATASET_TRAINING,
                  YOLO_DATASET_VALIDATIONS, ARGS_YOLO_VERSION, YOLO_DATASET_IMAGES)
from yolo.args import add_yolo_input_model_argument, add_yolo_version_argument
from yolo.files import (get_dataset_model_dir_path, get_model_best_onnx_path,
                        get_model_hailo_suite_dir_path, get_hailo_suite_calib_file_path)


# Remove the YOLO training and validations folders from the dataset, create the calibration set and copy the best ONNX weights to the Hailo Suite folder
def after_training(input_dir, calib_set_file_path, model_hailo_suite_dir, best_onnx_weights_path):
    # Get the training folder to the Hailo Suite folder
    input_training_images_path = os.path.join(input_dir, YOLO_DATASET_TRAINING, YOLO_DATASET_IMAGES)

    # Generate the .npy file to the Hailo Suite folder
    preprocess_images_to_npy(input_training_images_path, calib_set_file_path)

    # Remove the training and validations folder
    for folder in [YOLO_DATASET_TRAINING, YOLO_DATASET_VALIDATIONS]:
        folder_path = os.path.join(input_dir, folder)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
            print(f'Removed {folder} folder from {input_dir} folder')
        else:
            print(f'{folder} folder does not exist in {input_dir}')

    # Copy the best ONNX weights to the model Hailo Suite folder
    if os.path.exists(best_onnx_weights_path):
        shutil.copy(best_onnx_weights_path, model_hailo_suite_dir)
        print(f'Copied {best_onnx_weights_path} to {model_hailo_suite_dir} folder')
    else:
        print(f'{best_onnx_weights_path} does not exist')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to removed the unnecessary files and prepare the dataset for Hailo with calibration set')
    add_yolo_input_model_argument(parser)
    add_yolo_version_argument(parser)
    args = parse_args_as_dict(parser)

    # Get the YOLO input model
    arg_yolo_input_model = get_attribute_from_args(args, ARGS_YOLO_INPUT_MODEL)
    
    # Get the YOLO version
    arg_yolo_version = get_attribute_from_args(args, ARGS_YOLO_VERSION)

    # Get the dataset paths
    organized_dir = get_dataset_model_dir_path(YOLO_DATASET_ORGANIZED, None, arg_yolo_input_model)

    # Get the Hailo Suite calibration set file path
    calibration_set_file_path = get_hailo_suite_calib_file_path()

    # Get the model Hailo Suite path
    model_hailo_suite_dir = get_model_hailo_suite_dir_path(arg_yolo_input_model, arg_yolo_version)

    # Get the best weights path
    best_onnx_weights_path = get_model_best_onnx_path(arg_yolo_input_model, arg_yolo_version)

    # Move the folders
    after_training(organized_dir, calibration_set_file_path, model_hailo_suite_dir, best_onnx_weights_path)
