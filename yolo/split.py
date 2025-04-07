import argparse
from opencv.image_split import split_dataset
from yolo import YOLO_DATASET_AUGMENTED_2C_TO_PROCESS, YOLO_DATASET_ORGANIZED_2C_TO_PROCESS, \
    YOLO_DATASET_AUGMENTED_2C_PROCESSED, ARGS_YOLO_MODEL, ARGS_YOLO_MODEL_2C, ARGS_YOLO_MODEL_4C, ARGS_YOLO_MODEL_PROP, \
    YOLO_DATASET_AUGMENTED_4C_TO_PROCESS, YOLO_DATASET_AUGMENTED_4C_PROCESSED, \
    YOLO_DATASET_ORGANIZED_4C_TO_PROCESS

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to split YOLO dataset images and labels')
    parser.add_argument(ARGS_YOLO_MODEL, type=str, required=True, help='YOLO model',
                        choices=[ARGS_YOLO_MODEL_2C, ARGS_YOLO_MODEL_4C])
    args = parser.parse_args()

    # Get the YOLO model
    arg_yolo_model = getattr(args, ARGS_YOLO_MODEL_PROP)

    # Split the images
    if arg_yolo_model == ARGS_YOLO_MODEL_2C:
        split_dataset(YOLO_DATASET_AUGMENTED_2C_TO_PROCESS, YOLO_DATASET_ORGANIZED_2C_TO_PROCESS,
                      YOLO_DATASET_AUGMENTED_2C_PROCESSED)

    else:
        split_dataset(YOLO_DATASET_AUGMENTED_4C_TO_PROCESS, YOLO_DATASET_ORGANIZED_4C_TO_PROCESS,
                      YOLO_DATASET_AUGMENTED_4C_PROCESSED)
