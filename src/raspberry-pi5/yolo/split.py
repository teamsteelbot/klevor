import argparse

from args.args import get_attribute_from_args
from opencv.image_split import split_dataset
from yolo import (ARGS_YOLO_INPUT_MODEL, YOLO_DATASET_AUGMENTED, YOLO_DATASET_ORGANIZED, YOLO_DATASET_TO_PROCESS, YOLO_DATASET_PROCESSED)
from yolo.args import add_yolo_input_model_argument
from yolo.files import get_dataset_model_dir_path

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to split YOLO dataset images and labels')
    add_yolo_input_model_argument(parser)
    args = parser.parse_args()

    # Get the YOLO input model
    arg_yolo_input_model = get_attribute_from_args(args, ARGS_YOLO_INPUT_MODEL)

    # Get the dataset paths
    augmented_dir = get_dataset_model_dir_path(YOLO_DATASET_AUGMENTED, None, arg_yolo_input_model)
    organized_dir = get_dataset_model_dir_path(YOLO_DATASET_ORGANIZED, None, arg_yolo_input_model)

    # Split the images
    split_dataset(augmented_dir, organized_dir)
