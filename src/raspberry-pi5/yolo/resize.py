from opencv import DEFAULT_SIZE
from opencv.image_resize import resize_image
from yolo import (YOLO_DATASET_ORIGINAL, YOLO_DATASET_PROCESSED, YOLO_DATASET_RESIZED, YOLO_DATASET_TO_PROCESS)
from yolo.files import get_dataset_model_dir_path

if __name__ == '__main__':
    # Get the dataset paths
    original_to_process_dir = get_dataset_model_dir_path(YOLO_DATASET_ORIGINAL, YOLO_DATASET_TO_PROCESS)
    resized_to_process_dir = get_dataset_model_dir_path(YOLO_DATASET_RESIZED, YOLO_DATASET_TO_PROCESS)
    original_processed_dir = get_dataset_model_dir_path(YOLO_DATASET_ORIGINAL, YOLO_DATASET_PROCESSED)

    # Resize the images
    resize_image(original_to_process_dir, resized_to_process_dir, DEFAULT_SIZE, original_processed_dir)
