from argparse import ArgumentParser
import os
import shutil

from ..args import Args, Flag
from ..files import Files
from ..files.constants import DATASET_TRAINING
from ...files.constants import HAILO_SUITE_DIR

def after_compilation(model_name: str, yolo_version: str, hailo_suite_dir: str | os.PathLike[str]) -> None:
    """
    Copy files from the Hailo Model Zoo folder and remove the training folder from the model Hailo Suite folder.

    Args:
        model_name (str): Name of the YOLO model.
        yolo_version (str): Version of the YOLO model.
        hailo_suite_dir (str | os.PathLike[str]): Path to the Hailo Suite directory.
    """
    # Get the parsed, optimized, and compiled file paths
    model_hailo_suite_parsed_file_path = Files.get_model_hailo_suite_parsed_har_file_path(model_name, yolo_version)
    model_weights_parsed_har_file_path = Files.get_model_weights_parsed_har_file_path(model_name, yolo_version)
    model_hailo_suite_optimized_file_path = Files.get_model_hailo_suite_optimized_har_file_path(model_name,
                                                                                                yolo_version)
    model_weights_optimized_har_file_path = Files.get_model_weights_optimized_har_file_path(model_name, yolo_version)
    model_hailo_suite_compiled_file_path = Files.get_model_hailo_suite_compiled_hef_file_path(model_name, yolo_version)
    model_weights_compiled_hef_file_path = Files.get_model_weights_compiled_hef_file_path(model_name, yolo_version)

    # Get the training images folder from model Hailo Suite folder
    model_hailo_suite_training_dir = os.path.join(hailo_suite_dir, DATASET_TRAINING)

    # Remove the training images folder from the model Hailo Suite folder
    if os.path.exists(model_hailo_suite_training_dir):
        shutil.rmtree(model_hailo_suite_training_dir)
        print(f'Removed {DATASET_TRAINING} folder from {hailo_suite_dir} folder')
    else:
        print(f'{DATASET_TRAINING} folder does not exist in {hailo_suite_dir}')

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

if __name__ == '__main__':
    parser = ArgumentParser(
        description="Script to copy the generated '.har' and '.hef' files from the Hailo Suite folder")
    Args.add_yolo_input_model_argument(parser)
    Args.add_yolo_version_argument(parser)
    args = Args.parse_args_as_dict(parser)

    # Get the YOLO input model
    arg_yolo_input_model = Args.get_attribute_from_args_dict(args, Flag.INPUT_MODEL)

    # Get the YOLO version
    arg_yolo_version = Args.get_attribute_from_args_dict(args, Flag.VERSION)

    # Copy the files from the Hailo Model Zoo folder
    after_compilation(arg_yolo_input_model, arg_yolo_version, HAILO_SUITE_DIR)
