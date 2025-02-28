import random
from opencv.model_inference import preprocess, display_detections, outputs_to_image_bounding_boxes
import os
from opencv.constants import DEFAULT_SIZE, YOLO_TESTING, YOLO_IMAGES
from yolo.constants import YOLO_NUMBER_RANDOM_IMAGES

# Test random images from the given directory
def test_random_images(model, model_class_names:dict, run_inference_fn, input_organized_dir:str, draw_labels_name: bool,rgb_colors:dict[int, tuple[int, int, int]] = None):
    # Get testing folder
    input_images_testing_dir = os.path.join(input_organized_dir, YOLO_TESTING, YOLO_IMAGES)

    # Get some random images
    filenames = os.listdir(input_images_testing_dir)
    random_filenames = random.sample(filenames, YOLO_NUMBER_RANDOM_IMAGES)

    for random_filename in random_filenames:
        # Get the image path
        input_image_path = os.path.join(input_images_testing_dir, random_filename)
        print(f'Testing {input_image_path}')

        # Get the image
        original_image, preprocessed_image = preprocess(input_image_path, DEFAULT_SIZE)

        # Run inference
        outputs = run_inference_fn(model, preprocessed_image)

        # Print the detections
        print(outputs_to_image_bounding_boxes(outputs))

        # Display the image with the detections
        display_detections(model_class_names, preprocessed_image, outputs, draw_labels_name=draw_labels_name, rgb_colors=rgb_colors)
