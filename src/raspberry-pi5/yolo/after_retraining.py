import argparse
import os

from args.args import get_attribute_from_args
from files import move_folder
from yolo import (ARGS_YOLO_INPUT_MODEL, ARGS_YOLO_VERSION)
from yolo.args import add_yolo_input_model_argument, add_yolo_version_argument
from yolo.files import get_yolo_runs_dir_path, get_yolo_old_runs_dir_path, get_yolo_runs_dir_new_name_path

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to move YOLO model runs folder to old runs folder')
    add_yolo_input_model_argument(parser)
    add_yolo_version_argument(parser)
    args = parser.parse_args()

    # Get the YOLO input model
    arg_yolo_input_model = get_attribute_from_args(args, ARGS_YOLO_INPUT_MODEL)

    # Get the YOLO version
    arg_yolo_version = get_attribute_from_args(args, ARGS_YOLO_VERSION)

    # Get the runs folder path
    yolo_runs_dir = get_yolo_runs_dir_path(arg_yolo_version)

    # Get the runs folder path with the new name
    yolo_runs_new_name_dir = get_yolo_runs_dir_new_name_path(arg_yolo_version)

    # Check if the new name folder exists
    if os.path.exists(yolo_runs_new_name_dir):
        print(f'Error: The folder {yolo_runs_new_name_dir} already exists')
        exit(1)

    # Check if the runs folder exists
    if not os.path.exists(yolo_runs_dir):
        print(f"Error: The folder {yolo_runs_dir} doesn't exists")
        exit(1)

    # Rename the folder
    os.rename(yolo_runs_dir, yolo_runs_new_name_dir)

    # Get the old runs folder path
    yolo_old_runs_dir = get_yolo_old_runs_dir_path(arg_yolo_version)

    # Move the folder
    move_folder(yolo_runs_new_name_dir, yolo_old_runs_dir)
