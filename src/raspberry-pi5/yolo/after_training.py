import argparse
import os

from args.args import get_attribute_from_args
from files import move_folder
from yolo import (ARGS_YOLO_INPUT_MODEL, YOLO_DATASET_ORGANIZED, YOLO_DATASET_PROCESSED, YOLO_DATASET_TO_PROCESS,
                  YOLO_DATASET_TRAINING, YOLO_DATASET_VALIDATIONS)
from yolo.args import add_yolo_input_model_argument
from yolo.files import get_dataset_model_dir_path


# Remove the YOLO training and validation folders from the dataset
def after_training(input_dir):
    # Move the folders
    for folder in [YOLO_DATASET_TRAINING, YOLO_DATASET_VALIDATIONS]:
        folder_path = os.path.join(input_dir, folder)
        if os.path.exists(folder_path):
            os.remove(folder_path)
            print(f'Removed {folder} folder from {input_dir} folder')
        else:
            print(f'{folder} folder does not exist in {input_dir}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to set files as processed after YOLO model training')
    add_yolo_input_model_argument(parser)
    args = parser.parse_args()

    # Get the YOLO input model
    arg_yolo_input_model = get_attribute_from_args(args, ARGS_YOLO_INPUT_MODEL)

    # Get the dataset paths
    organized_dir = get_dataset_model_dir_path(YOLO_DATASET_ORGANIZED, None, arg_yolo_input_model)

    # Move the folders
    after_training(organized_dir)
