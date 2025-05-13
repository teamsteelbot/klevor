import argparse

from opencv.image_split import split_dataset
from yolo import (ARGS_YOLO_MODEL, YOLO_DATASET_AUGMENTED, YOLO_DATASET_ORGANIZED, YOLO_DATASET_TO_PROCESS, YOLO_DATASET_PROCESSED)
from yolo.args import add_yolo_model_argument
from yolo.files import get_dataset_model_dir_path

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to split YOLO dataset images and labels')
    add_yolo_model_argument(parser)
    args = parser.parse_args()

    # Get the YOLO model
    arg_yolo_model = getattr(args, ARGS_YOLO_MODEL)

    # Get the dataset paths
    augmented_to_process_dir = get_dataset_model_dir_path(YOLO_DATASET_AUGMENTED, YOLO_DATASET_TO_PROCESS, arg_yolo_model)
    organized_to_process_dir = get_dataset_model_dir_path(YOLO_DATASET_ORGANIZED, YOLO_DATASET_TO_PROCESS, arg_yolo_model)
    augmented_processed_dir = get_dataset_model_dir_path(YOLO_DATASET_AUGMENTED, YOLO_DATASET_PROCESSED, arg_yolo_model)

    # Split the images
    split_dataset(augmented_to_process_dir, organized_to_process_dir, augmented_processed_dir)
