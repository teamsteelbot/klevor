import os
import random

import numpy as np
import cv2

from files import ensure_path_exists
from opencv import DEFAULT_WIDTH, DEFAULT_HEIGHT, MAX_CALIB_SET_SAMPLES

def preprocess_images_to_npy(input_folder, output_file, target_shape=(DEFAULT_WIDTH, DEFAULT_HEIGHT, 3))->None:
    """
    Preprocess images from a folder and save them as a .npy file.

    Args:
        input_folder (str): Path to the folder containing images.
        output_file (str): Path where the .npy file will be saved.
        target_shape (tuple): Desired shape of the images (height, width, channels).
    """
    # Ensure the output directory exists
    ensure_path_exists(output_file)

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
        image = cv2.imread(image_path)

        if image is None:
            print(f"Warning: Unable to read {image_path}. Skipping...")
            continue

        # Resize the image to the target shape
        resized_image = cv2.resize(image, (w, h))

        # Ensure the image has the correct number of channels
        if resized_image.shape[-1] != c:
            print(f"Warning: {image_path} has unexpected channels. Skipping...")
            continue

        # Add the preprocessed image to the array
        images_array[counter] = resized_image
        counter += 1

    # Save the array to a .npy file
    np.save(output_file, images_array)
    print(f"Saved preprocessed images to {output_file}")