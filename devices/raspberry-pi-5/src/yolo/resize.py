from ..opencv import OpenCV
from .files import Files

if __name__ == '__main__':
    # Get the dataset paths
    original_to_process_dir = Files.get_dataset_model_dir_path(Files.DATASET_ORIGINAL, Files.DATASET_TO_PROCESS, None)
    resized_to_process_dir = Files.get_dataset_model_dir_path(Files.DATASET_RESIZED, Files.DATASET_TO_PROCESS, None)
    original_processed_dir = Files.get_dataset_model_dir_path(Files.DATASET_ORIGINAL, Files.DATASET_PROCESSED, None)

    # Resize the images
    OpenCV.resize_images(original_to_process_dir, resized_to_process_dir, original_processed_dir)

