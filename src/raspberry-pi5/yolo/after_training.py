from argparse import ArgumentParser
import os
import shutil

from yolo.args import Args
from yolo.files import Files


def after_training(input_dir, hailo_suite_dir, model_hailo_suite_dir, best_onnx_weights_path):
    """
    Remove the YOLO training and validation folders from the dataset, move the training folder and copy the best ONNX weights to the Hailo Suite folder.
    """
    # Move the training folder to the Hailo Suite folder
    input_training_images_path = os.path.join(input_dir, Files.DATASET_TRAINING, Files.DATASET_IMAGES)
    output_training_path = os.path.join(hailo_suite_dir, Files.DATASET_TRAINING)
    if os.path.exists(input_training_images_path):
        Files.move_folder_content(input_training_images_path, output_training_path)
        print(f'Moved {Files.DATASET_TRAINING} folder from {input_dir} folder to {output_training_path} folder')
    else:
        print(f'{Files.DATASET_TRAINING} folder does not exist in {input_dir}')

    # Remove the training and validations folder
    for folder in [Files.DATASET_TRAINING, Files.DATASET_VALIDATIONS]:
        folder_path = os.path.join(input_dir, folder)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
            print(f'Removed {folder} folder from {input_dir} folder')
        else:
            print(f'{folder} folder does not exist in {input_dir}')

    # Copy the best ONNX weights to the model Hailo Suite folder
    Files.ensure_path_exists(model_hailo_suite_dir)
    if os.path.exists(best_onnx_weights_path):
        shutil.copy(best_onnx_weights_path, model_hailo_suite_dir)
        print(f'Copied {best_onnx_weights_path} to {model_hailo_suite_dir} folder')
    else:
        print(f'{best_onnx_weights_path} does not exist')


def main() -> None:
    """
    Main function to run the script.
    """
    parser = ArgumentParser(
        description='Script to removed the unnecessary files and prepare the dataset for Hailo')
    Args.add_yolo_input_model_argument(parser)
    Args.add_yolo_version_argument(parser)
    args = Args.parse_args_as_dict(parser)

    # Get the YOLO input model
    arg_yolo_input_model = Args.get_attribute_from_args(args, Args.INPUT_MODEL)

    # Get the YOLO version
    arg_yolo_version = Args.get_attribute_from_args(args, Args.VERSION)

    # Get the dataset paths
    organized_dir = Files.get_dataset_model_dir_path(Files.DATASET_ORGANIZED, None, arg_yolo_input_model)

    # Get the Hailo Suite path
    hailo_suite_dir = Files.get_hailo_suite_dir_path()

    # Get the model Hailo Suite path
    model_hailo_suite_dir = Files.get_model_hailo_suite_dir_path(arg_yolo_input_model, arg_yolo_version)

    # Get the best weights path
    best_onnx_weights_path = Files.get_model_best_onnx_path(arg_yolo_input_model, arg_yolo_version)

    # Move the folders
    after_training(organized_dir, hailo_suite_dir, model_hailo_suite_dir, best_onnx_weights_path)


if __name__ == '__main__':
    main()
