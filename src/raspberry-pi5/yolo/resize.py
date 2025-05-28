from opencv.resize import resize_image
from yolo.files import Files


def main() -> None:
    """
    Main function to run the script.
    """
    # Get the dataset paths
    original_to_process_dir = Files.get_dataset_model_dir_path(Files.DATASET_ORIGINAL, Files.DATASET_TO_PROCESS, None)
    resized_to_process_dir = Files.get_dataset_model_dir_path(Files.DATASET_RESIZED, Files.DATASET_TO_PROCESS, None)
    original_processed_dir = Files.get_dataset_model_dir_path(Files.DATASET_ORIGINAL, Files.DATASET_PROCESSED, None)

    # Resize the images
    resize_image(original_to_process_dir, resized_to_process_dir, original_processed_dir)


if __name__ == '__main__':
    main()
