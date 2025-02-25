from opencv.image_resize import resize_image
import os

if __name__ == '__main__':
    # Set the input and output directories
    cwd = os.getcwd()
    base_dir = os.path.join(cwd, 'yolo', 'dataset')
    input_to_process_dir = os.path.join(base_dir, 'original', 'to_process')
    output_processed_dir = os.path.join(base_dir, 'original', 'processed')
    output_manipulated_dir = os.path.join(base_dir, 'resized', 'to_process')

    # Set the desired new dimensions
    width = 640
    height = 640

    # Resize images
    resize_image(input_to_process_dir, output_processed_dir, (width, height), output_manipulated_dir)
