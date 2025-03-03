import argparse
import os
from opencv.constants import YOLO_TRAINING, YOLO_VALIDATIONS
from files.files import move_folder
from yolo.constants import ARGS_YOLO_MODEL, ARGS_YOLO_MODEL_2C, ARGS_YOLO_MODEL_4C, ARGS_YOLO_MODEL_PROP
from yolo.constants import YOLO_DATASET_ORGANIZED_2C_TO_PROCESS, YOLO_DATASET_ORGANIZED_2C_PROCESSED
from yolo.constants import YOLO_DATASET_ORGANIZED_4C_TO_PROCESS, YOLO_DATASET_ORGANIZED_4C_PROCESSED


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

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Script to set files as processed after YOLO model training')
    parser.add_argument(ARGS_YOLO_MODEL, type=str, required=True, help='YOLO model', choices=[ARGS_YOLO_MODEL_2C, ARGS_YOLO_MODEL_4C])
    args = parser.parse_args()

    # Get the YOLO model
    arg_yolo_model = getattr(args, ARGS_YOLO_MODEL_PROP)

    # Move the folders
    if arg_yolo_model == ARGS_YOLO_MODEL_2C:
        move_folders(YOLO_DATASET_ORGANIZED_2C_TO_PROCESS, YOLO_DATASET_ORGANIZED_2C_PROCESSED)

    else:
        move_folders(YOLO_DATASET_ORGANIZED_4C_TO_PROCESS, YOLO_DATASET_ORGANIZED_4C_PROCESSED)