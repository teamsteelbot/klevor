import argparse
import os
import shutil

from opencv.calibration_set import preprocess_images_to_npy
from yolo.args import Args
from yolo.files import Files


def after_training(input_dir: str, calib_set_file_path: str, model_hailo_suite_dir: str, best_onnx_weights_path: str):
    """
    Remove the YOLO training and validations folders from the dataset, create the calibration set and copy the best ONNX weights to the Hailo Suite folder.

    Args:
        input_dir (str): Path to the input directory containing the YOLO dataset.
        calib_set_file_path (str): Path to save the calibration set .npy file.
        model_hailo_suite_dir (str): Path to the Hailo Suite folder for the model.
        best_onnx_weights_path (str): Path to the best ONNX weights file.

    Returns:
        None.
    """
    # Get the training folder to the Hailo Suite folder
    input_training_images_path = os.path.join(input_dir, Files.DATASET_TRAINING, Files.DATASET_IMAGES)

    # Generate the .npy file to the Hailo Suite folder
    preprocess_images_to_npy(input_training_images_path, calib_set_file_path)

    # Remove the training and validations folder
    for folder in [Files.DATASET_TRAINING, Files.DATASET_VALIDATIONS]:
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


def main() -> None:
    """
    Main function to run the script.
    """
    parser = argparse.ArgumentParser(
        description='Script to removed the unnecessary files and prepare the dataset for Hailo with calibration set')
    Args.add_yolo_input_model_argument(parser)
    Args.add_yolo_version_argument(parser)
    args = Args.parse_args_as_dict(parser)

    # Get the YOLO input model
    arg_yolo_input_model = Args.get_attribute_from_args(args, Args.INPUT_MODEL)

    # Get the YOLO version
    arg_yolo_version = Args.get_attribute_from_args(args, Args.VERSION)

    # Get the dataset paths
    organized_dir = Files.get_dataset_model_dir_path(Files.DATASET_ORGANIZED, None, arg_yolo_input_model)

    # Get the Hailo Suite calibration set file path
    calibration_set_file_path = Files.get_hailo_suite_calib_file_path()

    # Get the model Hailo Suite path
    model_hailo_suite_dir = Files.get_model_hailo_suite_dir_path(arg_yolo_input_model, arg_yolo_version)

    # Get the best weights path
    best_onnx_weights_path = Files.get_model_best_onnx_path(arg_yolo_input_model, arg_yolo_version)

    # Move the folders
    after_training(organized_dir, calibration_set_file_path, model_hailo_suite_dir, best_onnx_weights_path)


if __name__ == '__main__':
    main()
