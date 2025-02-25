import os
from opencv.image_split import split_images

if __name__ == '__main__':
    # Set the input and output directories
    cwd = os.getcwd()
    base_dir = os.path.join(cwd, 'yolo', 'dataset')
    input_to_process_dir = os.path.join(base_dir, 'augmented', 'to_process')
    output_organized_dir = os.path.join(base_dir, 'organized', 'to_process')
    output_processed_dir = os.path.join(base_dir, 'augmented', 'processed')

    split_images(input_to_process_dir, output_organized_dir, output_processed_dir)
