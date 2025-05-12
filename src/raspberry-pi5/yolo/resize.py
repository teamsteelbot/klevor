import os

from opencv import DEFAULT_SIZE
from opencv.image_resize import resize_image
from yolo import YOLO_DATASET, YOLO_DATASET_ORIGINAL, YOLO_PROCESSED, YOLO_DATASET_RESIZED, YOLO_TO_PROCESS

if __name__ == '__main__':
    # Get the dataset paths
    original_to_process = os.path.join(YOLO_DATASET, YOLO_DATASET_ORIGINAL, YOLO_TO_PROCESS)
    resized_to_process = os.path.join(YOLO_DATASET, YOLO_DATASET_RESIZED, YOLO_TO_PROCESS)
    original_processed = os.path.join(YOLO_DATASET, YOLO_DATASET_ORIGINAL, YOLO_PROCESSED)

    # Resize the images
    resize_image(original_to_process, resized_to_process, DEFAULT_SIZE, original_processed)
