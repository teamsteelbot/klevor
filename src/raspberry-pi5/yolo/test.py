import argparse
import random

from args import get_attribute_from_args, parse_args_as_dict
from opencv.image_display_detections import preprocess, display_detections
from model.image_bounding_boxes import outputs_to_image_bounding_boxes
import os
from opencv import DEFAULT_SIZE
from yolo import (YOLO_NUMBER_RANDOM_IMAGES, YOLO_FORMAT_PT, YOLO_GR_COLORS, YOLO_BGOR_COLORS, ARGS_YOLO_INPUT_MODEL,
                  ARGS_YOLO_FORMAT, ARGS_YOLO_VERSION, YOLO_DATASET_ORGANIZED, YOLO_MODEL_BGOR,
                  YOLO_MODEL_GR, YOLO_GMR_COLORS, YOLO_DATASET_TESTING, YOLO_DATASET_IMAGES,
                  YOLO_MODEL_GMR)
from model.yolo import (load, get_class_names, run_inference)
from yolo.args import (add_yolo_input_model_argument, add_yolo_format_argument, add_yolo_version_argument)
from yolo.files import (get_dataset_model_dir_path, get_model_best_pt_path, get_model_weight_dir_path)


def test_random_images(model, model_class_names: dict, run_inference_fn, input_organized_dir: str,
                       draw_labels_name: bool, rgb_colors: dict[int, tuple[int, int, int]] = None,
                       image_size: tuple[int, int] = DEFAULT_SIZE):
    """
    Test random images from the given directory.
    """
    # Get testing folder
    input_images_testing_dir = os.path.join(input_organized_dir, YOLO_DATASET_TESTING, YOLO_DATASET_IMAGES)

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


def test_random_images_pt(input_model_path: str, output_organized_dir: str, colors: dict[int, tuple[int, int, int]],
                          image_size: tuple[int, int] = DEFAULT_SIZE):
    """
    Test random images from the given directory using the given PyTorch model.
    """
    model = load(input_model_path)
    model_class_names = get_class_names(model)
    test_random_images(model, model_class_names, run_inference, output_organized_dir, False, colors,
                       image_size=image_size)

def main() -> None:
    """
    Main function to run the script.
    """
    parser = argparse.ArgumentParser(description='Script to test YOLO model with a given format')
    add_yolo_input_model_argument(parser)
    add_yolo_format_argument(parser)
    add_yolo_version_argument(parser)
    args = parse_args_as_dict(parser)

    # Get the YOLO input model
    arg_yolo_input_model = get_attribute_from_args(args, ARGS_YOLO_INPUT_MODEL)

    # Get the YOLO format
    arg_yolo_format = get_attribute_from_args(args, ARGS_YOLO_FORMAT)

    # Get the YOLO version
    arg_yolo_version = get_attribute_from_args(args, ARGS_YOLO_VERSION)

    # Load a model
    model_path = get_model_best_pt_path(arg_yolo_input_model, arg_yolo_version)
    model = load(model_path)

    # Get the model weights path
    model_weights_path = get_model_weight_dir_path(arg_yolo_input_model, arg_yolo_version)

    # Get the required dataset folder name
    organized_dir = get_dataset_model_dir_path(YOLO_DATASET_ORGANIZED, None, arg_yolo_input_model)

    # Get the dataset paths
    weights_best_pt = get_model_best_pt_path(arg_yolo_input_model, arg_yolo_version)

    # Get the class colors
    yolo_colors = None
    if arg_yolo_input_model == YOLO_MODEL_GR:
        if arg_yolo_format == YOLO_FORMAT_PT:
            yolo_colors = YOLO_GR_COLORS

    elif arg_yolo_input_model == YOLO_MODEL_GMR:
        if arg_yolo_format == YOLO_FORMAT_PT:
            yolo_colors = YOLO_GMR_COLORS

    elif arg_yolo_input_model == YOLO_MODEL_BGOR:
        if arg_yolo_format == YOLO_FORMAT_PT:
            yolo_colors = YOLO_BGOR_COLORS

    test_random_images_pt(weights_best_pt, organized_dir, yolo_colors)

if __name__ == '__main__':
    main()