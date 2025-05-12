import argparse
import os

from model.model_yolo import get_dataset_model_name
from opencv.image_augmentation import augment_dataset
from yolo import (YOLO_NUM_AUGMENTATIONS, ARGS_YOLO_MODEL, YOLO_DATASET,
                  YOLO_DATASET_LABELED, YOLO_DATASET_AUGMENTED, YOLO_TO_PROCESS, YOLO_PROCESSED)
from yolo.args import add_yolo_model_argument

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to augment YOLO model')
    add_yolo_model_argument(parser)
    args = parser.parse_args()

    # Get the YOLO model
    arg_yolo_model = getattr(args, ARGS_YOLO_MODEL)

    # Get the required dataset folder name
    labeled_name = get_dataset_model_name(YOLO_DATASET_LABELED, arg_yolo_model)
    augmented_name = get_dataset_model_name(YOLO_DATASET_AUGMENTED, arg_yolo_model)

    # Get the dataset paths
    labeled_to_process = os.path.join(YOLO_DATASET, labeled_name, YOLO_TO_PROCESS)
    labeled_processed = os.path.join(YOLO_DATASET, labeled_name, YOLO_PROCESSED)
    augmented_to_process = os.path.join(YOLO_DATASET, augmented_name, YOLO_TO_PROCESS)

    # Augment the dataset
    augment_dataset(labeled_to_process, labeled_processed, YOLO_NUM_AUGMENTATIONS, augmented_to_process)