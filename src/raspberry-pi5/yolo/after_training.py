import argparse
import os

from args.args import get_attribute_from_args
from files import move_folder
from yolo import (ARGS_YOLO_MODEL, YOLO_DATASET_ORGANIZED, YOLO_DATASET_PROCESSED, YOLO_DATASET_TO_PROCESS,
                  YOLO_DATASET_TRAINING, YOLO_DATASET_VALIDATIONS)
from yolo.args import add_yolo_model_argument
from yolo.files import get_dataset_model_dir_path


# Move the folders from the organized dataset to the processed dataset
def move_folders(input_base_dir, output_base_dir):
    # Move the folders
    for folder in [YOLO_DATASET_TRAINING, YOLO_DATASET_VALIDATIONS]:
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
    arg_yolo_model = get_attribute_from_args(args, ARGS_YOLO_MODEL)

    # Get the dataset paths
    organized_to_process_dir = get_dataset_model_dir_path(YOLO_DATASET_ORGANIZED, YOLO_DATASET_TO_PROCESS, arg_yolo_model)
    organized_processed_dir = get_dataset_model_dir_path(YOLO_DATASET_ORGANIZED, YOLO_DATASET_PROCESSED, arg_yolo_model)

    # Move the folders
    move_folders(organized_to_process_dir, organized_processed_dir)
