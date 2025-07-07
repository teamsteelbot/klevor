from ..files import Files
from ..files.constants import (
    DATASET_ORIGINAL,
    DATASET_PROCESSED,
    DATASET_RESIZED,
    DATASET_TO_PROCESS,
)
from ...opencv import OpenCV

if __name__ == '__main__':
    # Get the dataset paths
    original_to_process_dir = Files.get_dataset_model_dir_path(
        DATASET_ORIGINAL,
        DATASET_TO_PROCESS,
        None
    )
    resized_to_process_dir = Files.get_dataset_model_dir_path(
        DATASET_RESIZED,
        DATASET_TO_PROCESS,
        None
    )
    original_processed_dir = Files.get_dataset_model_dir_path(
        DATASET_ORIGINAL,
        DATASET_PROCESSED,
        None
    )

    # Resize the images
    OpenCV.resize_images(
        original_to_process_dir, resized_to_process_dir,
        original_processed_dir
    )
