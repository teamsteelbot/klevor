import random
from opencv.model_testing import load_pt_model, run_pt_inference, preprocess, display_detections, \
    outputs_to_image_bounding_boxes
import os
from opencv.constants import DEFAULT_SIZE
from yolo.constants import YOLO_NUMBER_RANDOM_IMAGES

# Test random images from the given directory
def test_random_images(model, model_class_names:dict, run_inference_fn, input_images_dir:str):
    # Get some random images
    filenames = os.listdir(input_images_dir)
    random_filenames = random.sample(filenames, YOLO_NUMBER_RANDOM_IMAGES)

    for random_filename in random_filenames:
        # Get the image path
        input_image_path = os.path.join(input_images_dir, random_filename)
        print(f'Testing {input_image_path}')

        # Get the image
        original_image, preprocessed_image = preprocess(input_image_path, DEFAULT_SIZE)

        # Run inference
        outputs = run_inference_fn(model, preprocessed_image)

        # Print the detections
        print(f'Detections for {input_image_path}')
        print(outputs_to_image_bounding_boxes(outputs))

        # Display the image with the detections
        display_detections(model_class_names, preprocessed_image, outputs, draw_labels_name=False, rgb_colors=YOLO_CLASS_COLORS)
