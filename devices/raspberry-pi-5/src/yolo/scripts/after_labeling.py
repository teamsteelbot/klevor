from ..files import Files

from ..files.constants import DATASET_RESIZED, DATASET_TO_PROCESS, \
    DATASET_PROCESSED

if __name__ == '__main__':
    # Get the resized to process folder
    resized_to_process_dir = Files.get_dataset_model_dir_path(DATASET_RESIZED,
                                                              DATASET_TO_PROCESS,
                                                              None)

    # Get the resized processed folder
    resized_processed_dir = Files.get_dataset_model_dir_path(DATASET_RESIZED,
                                                             DATASET_PROCESSED,
                                                             None)

    # Move the folder content
    Files.move_folder_content(resized_to_process_dir, resized_processed_dir)
