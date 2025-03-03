import random
from opencv.image_display_detections import preprocess, display_detections
from model.image_bounding_boxes import outputs_to_image_bounding_boxes
import os
from opencv.constants import DEFAULT_SIZE, YOLO_TESTING, YOLO_IMAGES
from yolo.constants import YOLO_NUMBER_RANDOM_IMAGES
from model.model_yolo import load, get_class_names, run_inference

# Test random images from the given directory
def test_random_images(model, model_class_names:dict, run_inference_fn, input_organized_dir:str, draw_labels_name: bool,rgb_colors:dict[int, tuple[int, int, int]] = None, image_size:tuple[int,int]=DEFAULT_SIZE):
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
        original_image, preprocessed_image = preprocess(input_image_path, image_size)

        # Run inference
        outputs = run_inference_fn(model, preprocessed_image)

        # Print the detections
        image_bounding_boxes = outputs_to_image_bounding_boxes(outputs)
        print(image_bounding_boxes)

        # Display the image with the detections
        display_detections(model_class_names, preprocessed_image, image_bounding_boxes, draw_labels_name=draw_labels_name, rgb_colors=rgb_colors)


# Test random images from the given directory using the given PyTorch model
def test_random_images_pt(input_model_path:str, output_organized_dir:str, colors:dict[int, tuple[int, int, int]], image_size:tuple[int,int]=DEFAULT_SIZE):
    model = load(input_model_path)
    model_class_names = get_class_names(model)
    test_random_images(model, model_class_names, run_inference, output_organized_dir, False, colors, image_size=image_size)

