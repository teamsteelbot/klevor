import argparse
import random
from opencv.image_display_detections import preprocess, display_detections
from model.image_bounding_boxes import outputs_to_image_bounding_boxes
import os
from opencv import DEFAULT_SIZE, YOLO_TESTING, YOLO_IMAGES
from yolo import YOLO_NUMBER_RANDOM_IMAGES, ARGS_YOLO_MODEL, ARGS_YOLO_MODEL_2C, ARGS_YOLO_MODEL_4C, \
    ARGS_YOLO_FORMAT, ARGS_YOLO_FORMAT_PT, ARGS_YOLO_QUANTIZED, ARGS_YOLO_MODEL_PROP, ARGS_YOLO_FORMAT_PROP, \
    ARGS_YOLO_QUANTIZED_PROP, \
    YOLO_RUNS_2C_WEIGHTS_BEST_PT, YOLO_RUNS_4C_WEIGHTS_BEST_PT, YOLO_DATASET_ORGANIZED_2C_TO_PROCESS, \
    YOLO_DATASET_ORGANIZED_4C_TO_PROCESS, YOLO_2C_COLORS, YOLO_4C_COLORS
from model.model_yolo import load, get_class_names, run_inference


# Test random images from the given directory
def test_random_images(model, model_class_names: dict, run_inference_fn, input_organized_dir: str,
                       draw_labels_name: bool, rgb_colors: dict[int, tuple[int, int, int]] = None,
                       image_size: tuple[int, int] = DEFAULT_SIZE):
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
        display_detections(model_class_names, preprocessed_image, image_bounding_boxes,
                           draw_labels_name=draw_labels_name, rgb_colors=rgb_colors)


# Test random images from the given directory using the given PyTorch model
def test_random_images_pt(input_model_path: str, output_organized_dir: str, colors: dict[int, tuple[int, int, int]],
                          image_size: tuple[int, int] = DEFAULT_SIZE):
    model = load(input_model_path)
    model_class_names = get_class_names(model)
    test_random_images(model, model_class_names, run_inference, output_organized_dir, False, colors,
                       image_size=image_size)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to test YOLO model with a given format')
    parser.add_argument(ARGS_YOLO_MODEL, type=str, required=True, help='YOLO model',
                        choices=[ARGS_YOLO_MODEL_2C, ARGS_YOLO_MODEL_4C])
    parser.add_argument(ARGS_YOLO_FORMAT, type=str, required=True, help='YOLO format',
                        choices=[ARGS_YOLO_FORMAT_PT])
    parser.add_argument(ARGS_YOLO_QUANTIZED, type=bool, required=False, help='YOLO model quantization')
    args = parser.parse_args()

    # Get the YOLO model
    arg_yolo_model = getattr(args, ARGS_YOLO_MODEL_PROP)

    # Get the YOLO format
    arg_yolo_format = getattr(args, ARGS_YOLO_FORMAT_PROP)

    # Get the YOLO quantization
    arg_yolo_quantized = getattr(args, ARGS_YOLO_QUANTIZED_PROP)
    if arg_yolo_quantized is None:
        arg_yolo_quantized = False

    # Load a model
    model_path = None
    if arg_yolo_model == ARGS_YOLO_MODEL_2C:
        if arg_yolo_format == ARGS_YOLO_FORMAT_PT:
            model_path = YOLO_RUNS_2C_WEIGHTS_BEST_PT

    elif arg_yolo_model == ARGS_YOLO_MODEL_4C:
        if arg_yolo_format == ARGS_YOLO_FORMAT_PT:
            model_path = YOLO_RUNS_4C_WEIGHTS_BEST_PT
    model = load(model_path)

    if arg_yolo_model == ARGS_YOLO_MODEL_2C:
        if arg_yolo_format == ARGS_YOLO_FORMAT_PT:
            test_random_images_pt(YOLO_RUNS_2C_WEIGHTS_BEST_PT, YOLO_DATASET_ORGANIZED_2C_TO_PROCESS, YOLO_2C_COLORS)

    elif arg_yolo_model == ARGS_YOLO_MODEL_4C:
        if arg_yolo_format == ARGS_YOLO_FORMAT_PT:
            test_random_images_pt(YOLO_RUNS_4C_WEIGHTS_BEST_PT, YOLO_DATASET_ORGANIZED_4C_TO_PROCESS, YOLO_4C_COLORS)
