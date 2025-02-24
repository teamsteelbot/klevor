import cv2
import os
import time
import files.files as files

# Resize image function
def resize_image(input_to_process_dir: str, output_manipulated_dir: str, width: int, height:int , output_processed_dir: str= None, interpolation=cv2.INTER_LINEAR):
    # Check if the path exists, if not it creates it
    if not os.path.exists(output_manipulated_dir):
        os.makedirs(output_manipulated_dir)

    # Set the new dimensions
    new_dim = (width, height)

    # Iterate over the files in the given path
    for filename in os.listdir(input_to_process_dir):
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            # Start timing
            start_time = time.time()

            # Read image
            image_path = os.path.join(input_to_process_dir, filename)
            image = cv2.imread(image_path)

            # Resize image
            resized_img = cv2.resize(image, new_dim, interpolation=interpolation)

            # Write back the image
            output_path = os.path.join(output_manipulated_dir, filename)
            cv2.imwrite(output_path, resized_img)

            # End timing
            end_time = time.time()
            elapsed_time = end_time - start_time

            # Log
            print(f'Resized and saved {filename} to {output_manipulated_dir} in {elapsed_time:.2f} seconds')
            
            # Check if the output_processed_dir is not None
            if output_processed_dir is not None:
                files.move_file(image_path, os.path.join(output_processed_dir, filename))