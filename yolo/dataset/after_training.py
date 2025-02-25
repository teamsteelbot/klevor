import os
from files.files import move_folder
from opencv.constants import TRAINING, VALIDATIONS

if __name__=='__main__':
    # Set input and output directories
    cwd=os.getcwd()
    base_dir=os.path.join(cwd, 'yolo', 'dataset', 'organized')
    input_to_process_base_dir=os.path.join(base_dir, 'to_process')
    output_processed_base_dir=os.path.join(base_dir, 'processed')

    # Move the folders
    for folder in [TRAINING, VALIDATIONS]:
        input_to_process_dir=os.path.join(input_to_process_base_dir, folder)
        output_processed_dir=os.path.join(output_processed_base_dir, folder)

        move_folder(input_to_process_dir, output_processed_dir)
        move_folder(input_to_process_dir, output_processed_dir)
