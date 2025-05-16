import argparse

from args.args import get_attribute_from_args, parse_args_as_dict
from opencv.image_augmentation import augment_dataset
from yolo import (YOLO_NUM_AUGMENTATIONS, ARGS_YOLO_INPUT_MODEL,
                  YOLO_DATASET_LABELED, YOLO_DATASET_AUGMENTED, YOLO_DATASET_TO_PROCESS, YOLO_DATASET_PROCESSED)
from yolo.args import add_yolo_input_model_argument
from yolo.files import get_dataset_model_dir_path

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to augment YOLO model')
    add_yolo_input_model_argument(parser)
    args = parse_args_as_dict(parser)

    # Get the YOLO input model
    arg_yolo_input_model = get_attribute_from_args(args, ARGS_YOLO_INPUT_MODEL)

    # Get the dataset paths
    labeled_to_process_dir = get_dataset_model_dir_path(YOLO_DATASET_LABELED, YOLO_DATASET_TO_PROCESS, arg_yolo_input_model)
    labeled_processed_dir = get_dataset_model_dir_path(YOLO_DATASET_LABELED, YOLO_DATASET_PROCESSED, arg_yolo_input_model)
    augmented_dir = get_dataset_model_dir_path(YOLO_DATASET_AUGMENTED, None, arg_yolo_input_model)

    # Augment the dataset
    augment_dataset(labeled_to_process_dir, augmented_dir, YOLO_NUM_AUGMENTATIONS, labeled_processed_dir)