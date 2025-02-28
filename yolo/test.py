import random
from opencv.model_testing import load_model, run_inference, preprocess, display_detections, \
    outputs_to_image_bounding_boxes
import os
from opencv.constants import IMAGES, DEFAULT_SIZE
from yolo.constants import YOLO_DATASET_ORGANIZED_TO_PROCESS, YOLO_RUNS_WEIGHTS_BEST_PT, YOLO_TESTING, YOLO_CLASS_COLORS

# Minimum confidence level and number of random images to test
MINIMUM_CONFIDENCE_LEVEL = 0.45
NUMBER_RANDOM_IMAGES = 10

if __name__ == '__main__':
    # Set the input and output directories
    input_to_process_test_dir = os.path.join(YOLO_DATASET_ORGANIZED_TO_PROCESS, YOLO_TESTING, IMAGES)

    # Load the model
    model = load_model(YOLO_RUNS_WEIGHTS_BEST_PT)

    # Get some random images
    filenames = os.listdir(input_to_process_test_dir)
    random_filenames = random.sample(filenames, NUMBER_RANDOM_IMAGES)

    for random_filename in random_filenames:
        # Get the image path
        input_image_path = os.path.join(input_to_process_test_dir, random_filename)
        print(f'Testing {input_image_path}')

        # Get the image
        original_image, preprocessed_image = preprocess(input_image_path, DEFAULT_SIZE)

        # Run inference
        outputs = run_inference(model, preprocessed_image)

        # Print the detections
        print(f'Detections for {input_image_path}')
        print(outputs_to_image_bounding_boxes(outputs))

        # Display the image with the detections
        display_detections(model, preprocessed_image, outputs, draw_labels_name=False, rgb_colors=YOLO_CLASS_COLORS)
