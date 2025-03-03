import argparse
from opencv.image_augmentation import augment_dataset
from yolo.constants import (YOLO_NUM_AUGMENTATIONS, YOLO_DATASET_LABELED_2C_PROCESSED, \
                            YOLO_DATASET_LABELED_2C_TO_PROCESS, YOLO_DATASET_AUGMENTED_2C_TO_PROCESS, \
                            YOLO_DATASET_LABELED_4C_PROCESSED, YOLO_DATASET_LABELED_4C_TO_PROCESS, \
                            YOLO_DATASET_AUGMENTED_4C_TO_PROCESS, ARGS_YOLO_MODEL, ARGS_YOLO_MODEL_2C,
                            ARGS_YOLO_MODEL_4C, ARGS_YOLO_MODEL_PROP)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to augment YOLO model')
    parser.add_argument(ARGS_YOLO_MODEL, type=str, required=True, help='YOLO model', choices=[ARGS_YOLO_MODEL_2C, ARGS_YOLO_MODEL_4C])
    args = parser.parse_args()

    # Get the YOLO model
    arg_yolo_model = getattr(args, ARGS_YOLO_MODEL_PROP)

    # Augment the dataset
    if arg_yolo_model == ARGS_YOLO_MODEL_2C:
        augment_dataset(YOLO_DATASET_LABELED_2C_TO_PROCESS, YOLO_DATASET_AUGMENTED_2C_TO_PROCESS, YOLO_NUM_AUGMENTATIONS,
                    YOLO_DATASET_LABELED_2C_PROCESSED)

    else:
        augment_dataset(YOLO_DATASET_LABELED_4C_TO_PROCESS, YOLO_DATASET_AUGMENTED_4C_TO_PROCESS, YOLO_NUM_AUGMENTATIONS,
                    YOLO_DATASET_LABELED_4C_PROCESSED)