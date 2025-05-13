import argparse

from opencv.image_augmentation import augment_dataset
from yolo import (YOLO_NUM_AUGMENTATIONS, ARGS_YOLO_MODEL,
                  YOLO_DATASET_LABELED, YOLO_DATASET_AUGMENTED, YOLO_DATASET_TO_PROCESS, YOLO_DATASET_PROCESSED)
from yolo.args import add_yolo_model_argument
from yolo.files import get_dataset_model_dir_path

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to augment YOLO model')
    add_yolo_model_argument(parser)
    args = parser.parse_args()

    # Get the YOLO model
    arg_yolo_model = getattr(args, ARGS_YOLO_MODEL)

    # Get the dataset paths
    labeled_to_process_dir = get_dataset_model_dir_path(YOLO_DATASET_LABELED, YOLO_DATASET_TO_PROCESS, arg_yolo_model)
    labeled_processed_dir = get_dataset_model_dir_path(YOLO_DATASET_LABELED, YOLO_DATASET_PROCESSED, arg_yolo_model)
    augmented_to_process_dir = get_dataset_model_dir_path(YOLO_DATASET_AUGMENTED, YOLO_DATASET_TO_PROCESS, arg_yolo_model)

    # Augment the dataset
    augment_dataset(labeled_to_process_dir, augmented_to_process_dir, YOLO_NUM_AUGMENTATIONS, labeled_processed_dir)