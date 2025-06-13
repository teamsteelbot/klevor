import os
import random

import cv2
import numpy as np

from files import Files
from opencv import MAX_CALIB_SET_SAMPLES
from opencv.preprocessing import Preprocessing


def preprocess_images_to_npy(input_folder, output_file, target_shape=Preprocessing.SHAPE) -> None:
    """
    Preprocess images from a folder and save them as a .npy file.

    Args:
        input_folder (str): Path to the folder containing images.
        output_file (str): Path where the .npy file will be saved.
        target_shape (tuple): Desired shape of the images (height, width, channels).
    """
    # Ensure the output directory exists
    Files.ensure_directory_exists(output_file)

    # Get the images
    calib_size = len(os.listdir(input_folder))  # Number of images
    if calib_size <= MAX_CALIB_SET_SAMPLES:
        image_files = enumerate(os.listdir(input_folder))
    else:
        calib_size = MAX_CALIB_SET_SAMPLES
        image_files = enumerate(random.sample(os.listdir(input_folder), MAX_CALIB_SET_SAMPLES))
    h, w, c = target_shape

    # Initialize an empty array to store preprocessed images
    images_array = np.zeros((calib_size, h, w, c), dtype=np.uint8)

    # Iterate through each image in the input folder
    counter = 0
    for _, image_name in image_files:
        image_path = os.path.join(input_folder, image_name)
        image = Preprocessing.load_image(image_path, image_size=(w, h), to_rgb=True, interpolation=cv2.INTER_LINEAR)

        # Add the preprocessed image to the array
        images_array[counter] = image
        counter += 1

    # Save the array to a .npy file
    np.save(output_file, images_array)
    print(f"Saved preprocessed images to {output_file}")
