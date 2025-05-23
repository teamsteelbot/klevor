import argparse

from args import parse_args_as_dict
from files import move_folder_content
from yolo import (YOLO_DATASET_RESIZED, YOLO_DATASET_TO_PROCESS, YOLO_DATASET_PROCESSED)
from yolo.files import get_dataset_model_dir_path

def main() -> None:
    """
    Main function to run the script.
    """
    parser = argparse.ArgumentParser(description='Script to move YOLO model resized to process folder content to processed folder')
    args = parse_args_as_dict(parser)

    # Get the resized to process folder
    resized_to_process_dir = get_dataset_model_dir_path(YOLO_DATASET_RESIZED, YOLO_DATASET_TO_PROCESS, None)

    # Get the resized processed folder
    resized_processed_dir = get_dataset_model_dir_path(YOLO_DATASET_RESIZED, YOLO_DATASET_PROCESSED, None)

    # Move the folder content
    move_folder_content(resized_to_process_dir, resized_processed_dir)

if __name__ == '__main__':
    main()