from argparse import ArgumentParser
import os
import shutil

from ..args import Args, Flags
from ..files import Files
from ..files.constants import DATASET_ORGANIZED, DATASET_TRAINING, DATASET_VALIDATIONS, DATASET_IMAGES
from ...hailo.constants import HAILO_SUITE_DIR

def after_training(input_dir: str | os.PathLike[str], hailo_suite_dir: str | os.PathLike[str],
                   model_hailo_suite_dir: str | os.PathLike[str], best_onnx_weights_path: str | os.PathLike[str]) -> None:
    """
    Remove the YOLO training and validation folders from the dataset, move the training folder and copy the best ONNX weights to the Hailo Suite folder.

    Args:
        input_dir (str | os.PathLike[str]): The path to the input directory containing the YOLO dataset.
        hailo_suite_dir (str | os.PathLike[str]): The path to the Hailo Suite directory.
        model_hailo_suite_dir (str | os.PathLike[str]): The path to the model Hailo Suite directory.
        best_onnx_weights_path (str | os.PathLike[str]): The path to the best ONNX weights file.
    """
    # Move the training folder to the Hailo Suite folder
    input_training_images_path = os.path.join(input_dir, DATASET_TRAINING, DATASET_IMAGES)
    output_training_path = os.path.join(hailo_suite_dir, DATASET_TRAINING)
    if os.path.exists(input_training_images_path):
        Files.move_folder_content(input_training_images_path, output_training_path)
        print(f'Moved {DATASET_TRAINING} folder from {input_dir} folder to {output_training_path} folder')
    else:
        print(f'{DATASET_TRAINING} folder does not exist in {input_dir}')

    # Remove the training and validations folder
    for folder in [DATASET_TRAINING, DATASET_VALIDATIONS]:
        folder_path = os.path.join(input_dir, folder)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
            print(f'Removed {folder} folder from {input_dir} folder')
        else:
            print(f'{folder} folder does not exist in {input_dir}')

    # Copy the best ONNX weights to the model Hailo Suite folder
    Files.ensure_directory_exists(model_hailo_suite_dir)
    if os.path.exists(best_onnx_weights_path):
        shutil.copy(best_onnx_weights_path, model_hailo_suite_dir)
        print(f'Copied {best_onnx_weights_path} to {model_hailo_suite_dir} folder')
    else:
        print(f'{best_onnx_weights_path} does not exist')


if __name__ == '__main__':
    parser = ArgumentParser(
        description='Script to removed the unnecessary files and prepare the dataset for Hailo')
    Args.add_yolo_input_model_argument(parser)
    Args.add_yolo_version_argument(parser)
    args = Args.parse_args_as_dict(parser)

    # Get the YOLO input model
    arg_yolo_input_model = Args.get_attribute_from_args_dict(args, Flags.INPUT_MODEL)

    # Get the YOLO version
    arg_yolo_version = Args.get_attribute_from_args_dict(args, Flags.VERSION)

    # Get the dataset paths
    organized_dir = Files.get_dataset_model_dir_path(DATASET_ORGANIZED, None, arg_yolo_input_model)

    # Get the model Hailo Suite path
    model_hailo_suite_dir = Files.get_model_hailo_suite_dir_path(arg_yolo_input_model, arg_yolo_version)

    # Get the best weights path
    best_onnx_weights_path = Files.get_model_best_onnx_path(arg_yolo_input_model, arg_yolo_version)

    # Move the folders
    after_training(organized_dir, HAILO_SUITE_DIR, model_hailo_suite_dir, best_onnx_weights_path)

