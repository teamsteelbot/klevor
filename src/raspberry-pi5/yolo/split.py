import argparse
import os.path

from model.model_yolo import get_dataset_model_name
from opencv.image_split import split_dataset
from yolo import (ARGS_YOLO_MODEL, YOLO_DATASET_AUGMENTED, YOLO_DATASET_ORGANIZED, YOLO_TO_PROCESS, YOLO_PROCESSED)
from yolo.args import add_yolo_model_argument

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to split YOLO dataset images and labels')
    add_yolo_model_argument(parser)
    args = parser.parse_args()

    # Get the YOLO model
    arg_yolo_model = getattr(args, ARGS_YOLO_MODEL)

    # Get the required dataset folder name
    augmented_name = get_dataset_model_name(YOLO_DATASET_AUGMENTED, arg_yolo_model)
    organized_name = get_dataset_model_name(YOLO_DATASET_ORGANIZED, arg_yolo_model)

    # Get the dataset paths
    augmented_to_process = os.path.join(YOLO_DATASET_AUGMENTED, augmented_name, YOLO_TO_PROCESS)
    organized_to_process = os.path.join(YOLO_DATASET_ORGANIZED, organized_name, YOLO_TO_PROCESS)
    augmented_processed = os.path.join(YOLO_DATASET_AUGMENTED, augmented_name, YOLO_PROCESSED)

    # Split the images
    split_dataset(augmented_to_process, organized_to_process, augmented_processed)
