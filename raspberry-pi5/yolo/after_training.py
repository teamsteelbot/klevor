import argparse
import os

from args.args import get_attribute_name
from model.model_yolo import get_dataset_model_name
from opencv import YOLO_TRAINING, YOLO_VALIDATIONS
from files import move_folder
from yolo import (ARGS_YOLO_MODEL, YOLO_DATASET_ORGANIZED, YOLO_PROCESSED, YOLO_TO_PROCESS)
from yolo.args import add_yolo_model_argument


# Move the folders from the organized dataset to the processed dataset
def move_folders(input_base_dir, output_base_dir):
    # Move the folders
    for folder in [YOLO_TRAINING, YOLO_VALIDATIONS]:
        # Set the input and output directories
        input_dir = os.path.join(input_base_dir, folder)
        output_dir = os.path.join(output_base_dir, folder)

        # Move the folder
        move_folder(input_dir, output_dir)

        # Log
        print(f'Moved {input_dir} to {output_dir}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to set files as processed after YOLO model training')
    add_yolo_model_argument(parser)
    args = parser.parse_args()

    # Get the YOLO model
    arg_yolo_model = getattr(args, get_attribute_name(ARGS_YOLO_MODEL))

    # Get the required dataset folder name
    organized_dataset_name = get_dataset_model_name(YOLO_DATASET_ORGANIZED, arg_yolo_model)

    # Get the dataset paths
    organized_to_process = os.path.join(YOLO_DATASET_ORGANIZED, organized_dataset_name, YOLO_TO_PROCESS)
    organized_processed = os.path.join(YOLO_DATASET_ORGANIZED, organized_dataset_name, YOLO_PROCESSED)

    # Move the folders
    move_folders(organized_to_process, organized_processed)
