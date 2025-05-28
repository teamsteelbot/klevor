import argparse
import os
import shutil

from yolo.args import Args
from yolo.files import Files


def after_compilation(model_name, yolo_version, hailo_suite_dir):
    """
    Copy files from the Hailo Model Zoo folder and remove the training folder from the model Hailo Suite folder.
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
    model_hailo_suite_training_dir = os.path.join(hailo_suite_dir, Files.DATASET_TRAINING)

    # Remove the training images folder from the model Hailo Suite folder
    if os.path.exists(model_hailo_suite_training_dir):
        shutil.rmtree(model_hailo_suite_training_dir)
        print(f'Removed {Files.DATASET_TRAINING} folder from {hailo_suite_dir} folder')
    else:
        print(f'{Files.DATASET_TRAINING} folder does not exist in {hailo_suite_dir}')

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
    Args.add_yolo_input_model_argument(parser)
    Args.add_yolo_version_argument(parser)
    args = Args.parse_args_as_dict(parser)

    # Get the YOLO input model
    arg_yolo_input_model = Args.get_attribute_from_args(args, Args.INPUT_MODEL)

    # Get the YOLO version
    arg_yolo_version = Args.get_attribute_from_args(args, Args.VERSION)

    # Get the Hailo Suite path
    hailo_suite_dir = Files.get_hailo_suite_dir_path()

    # Copy the files from the Hailo Model Zoo folder
    after_compilation(arg_yolo_input_model, arg_yolo_version, hailo_suite_dir)


if __name__ == '__main__':
    main()
