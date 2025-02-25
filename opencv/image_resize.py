import cv2
import os
import time
from files.files import move_file

# Resize image function
def resize_image(input_to_process_dir: str, output_resized_to_process_dir: str, new_image_size: tuple[int, int] , output_processed_dir: str= None, interpolation=cv2.INTER_LINEAR):
    # Check if the path exists, if not it creates it
    if not os.path.exists(output_resized_to_process_dir):
        os.makedirs(output_resized_to_process_dir)

    # Iterate over the files in the given path
    for filename in os.listdir(input_to_process_dir):
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            # Start timing
            start_time = time.time()

            # Read image
            image_path = os.path.join(input_to_process_dir, filename)
            image = cv2.imread(image_path)

            # Resize image
            resized_image = cv2.resize(image, new_image_size, interpolation=interpolation)

            # Write back the image
            output_path = os.path.join(output_resized_to_process_dir, filename)
            cv2.imwrite(output_path, resized_image)

            # End timing
            end_time = time.time()
            elapsed_time = end_time - start_time

            # Log
            print(f'Resized and saved {filename} to {output_resized_to_process_dir} in {elapsed_time:.2f} seconds')
            
            # Check if the output_processed_dir is not None
            if output_processed_dir is not None:
                move_file(image_path, os.path.join(output_processed_dir, filename))