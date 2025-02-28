from opencv.constants import YOLO_TRAINING, YOLO_VALIDATIONS
from files.files import move_folder
import os

# Move the folders from the organized dataset to the processed dataset
def move_folders(input_base_dir, output_base_dir):
    # Move the folders
    for folder in [YOLO_TRAINING, YOLO_VALIDATIONS]:
        # Set the input and output directories
        input_dir = os.path.join(input_base_dir, folder)
        output_dir = os.path.join(output_base_dir, folder)

        # Move the folder
        move_folder(input_dir, output_dir)

        # Log
        print(f'Moved {input_dir} to {output_dir}')
