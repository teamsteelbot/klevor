from typing import LiteralString

import cv2
import os
import time
from files import Files
from opencv.preprocessing import Preprocessing


def resize_image(input_to_process_dir: LiteralString, output_resized_to_process_dir: LiteralString,
                 new_image_size: tuple[int, int],
                 output_processed_dir: LiteralString = None, interpolation=cv2.INTER_LINEAR)->None:
    """
    Resize image function.

    Args:
        input_to_process_dir (str): Directory containing images to be resized.
        output_resized_to_process_dir (str): Directory where resized images will be saved.
        new_image_size (tuple[int, int]): New size for the images as (width, height).
        output_processed_dir (str, optional): Directory where original images will be moved after processing.
        interpolation: Interpolation method used for resizing.
    """
    # Check if the path exists, if not it creates it
    Files.ensure_path_exists(output_resized_to_process_dir)

    # Iterate over the files in the given path
    for filename in os.listdir(input_to_process_dir):
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            # Start timing
            start_time = time.time()

            # Read image
            image_path = os.path.join(input_to_process_dir, filename)
            image = Preprocessing.load_image(image_path, new_image_size, interpolation=interpolation)

            # Write back the image
            output_path = os.path.join(output_resized_to_process_dir, filename)
            cv2.imwrite(output_path, image)

            # End timing
            end_time = time.time()
            elapsed_time = end_time - start_time

            # Log
            print(f'Resized and saved {filename} to {output_resized_to_process_dir} in {elapsed_time:.2f} seconds')

            # Check if the output_processed_dir is not None
            if output_processed_dir is not None:
                Files.move_file(image_path, os.path.join(output_processed_dir, filename))
