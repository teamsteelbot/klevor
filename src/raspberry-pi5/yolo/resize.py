from opencv import DEFAULT_SIZE
from opencv.image_resize import resize_image
from yolo import (YOLO_DATASET_ORIGINAL, YOLO_DATASET_PROCESSED, YOLO_DATASET_RESIZED, YOLO_DATASET_TO_PROCESS)
from yolo.files import get_dataset_model_dir_path

# Main function to run the script
def main() -> None:
    # Get the dataset paths
    original_to_process_dir = get_dataset_model_dir_path(YOLO_DATASET_ORIGINAL, YOLO_DATASET_TO_PROCESS, None)
    resized_to_process_dir = get_dataset_model_dir_path(YOLO_DATASET_RESIZED, YOLO_DATASET_TO_PROCESS, None)
    original_processed_dir = get_dataset_model_dir_path(YOLO_DATASET_ORIGINAL, YOLO_DATASET_PROCESSED, None)

    # Resize the images
    resize_image(original_to_process_dir, resized_to_process_dir, DEFAULT_SIZE, original_processed_dir)

if __name__ == '__main__':
    main()