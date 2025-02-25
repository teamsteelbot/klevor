import os
from files.files import move_folder
from yolo.constants import YOLO_DATASET_ORGANIZED_PROCESSED, YOLO_DATASET_ORGANIZED_TO_PROCESS
from opencv.constants import TRAINING, VALIDATIONS

if __name__=='__main__':
    # Move the folders
    for folder in [TRAINING, VALIDATIONS]:
        # Set the input and output directories
        input_dir=os.path.join(YOLO_DATASET_ORGANIZED_TO_PROCESS, folder)
        output_dir=os.path.join(YOLO_DATASET_ORGANIZED_PROCESSED, folder)

        # Move the folder
        move_folder(input_dir, output_dir)
        move_folder(input_dir, output_dir)

        # Log
        print(f'Moved {input_dir} to {output_dir}')
