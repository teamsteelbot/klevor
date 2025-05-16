import argparse

from files import move_folder_content
from yolo import (YOLO_DATASET_RESIZED, YOLO_DATASET_TO_PROCESS, YOLO_DATASET_PROCESSED)
from yolo.files import get_dataset_model_dir_path

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to move YOLO model resized to process folder content to processed folder')
    args = parser.parse_args()

    # Get the resized to process folder
    resized_to_process_dir = get_dataset_model_dir_path(YOLO_DATASET_RESIZED, YOLO_DATASET_TO_PROCESS, None)

    # Get the resized processed folder
    resized_processed_dir = get_dataset_model_dir_path(YOLO_DATASET_RESIZED, YOLO_DATASET_PROCESSED, None)

    # Move the folder content
    move_folder_content(resized_to_process_dir, resized_processed_dir)
