import cv2
import os

# Resize image function
def resize_image(input_dir: str, output_dir: str, width: int, height:int , interpolation=cv2.INTER_LINEAR):
    # Check if the path exists, if not it creates it
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Set the new dimensions
    new_dim = (width, height)

    # Iterate over the files in the given path
    for filename in os.listdir(input_dir):
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            # Read image
            img_path = os.path.join(input_dir, filename)
            img = cv2.imread(img_path)

            # Resize image
            resized_img = cv2.resize(img, new_dim, interpolation=interpolation)

            # Write back the image
            output_path = os.path.join(output_dir, filename)
            cv2.imwrite(output_path, resized_img)

            # Log
            print(f'Resized and saved {filename} to {output_dir}')