import argparse
import os
import random

from model.image_bounding_boxes import ImageBoundingBoxes
from opencv.detections import Detections
from opencv.preprocessing import Preprocessing
from yolo import Yolo
from yolo.args import Args
from yolo.files import Files


def test_random_images(model, model_class_names: dict, run_inference_fn, input_organized_dir: str,
                       draw_labels_name: bool, rgb_colors: dict[int, tuple[int, int, int]] = None,
                       image_size: tuple[int, int] = Preprocessing.SIZE):
    """
    Test random images from the given directory.

    Args:
        model: The YOLO model to use for inference.
        model_class_names (dict): Dictionary mapping class indices to class names.
        run_inference_fn: Function to run inference on the preprocessed image.
        input_organized_dir (str): Directory containing organized dataset images.
        draw_labels_name (bool): Whether to draw labels on the detections.
        rgb_colors (dict[int, tuple[int, int, int]]): Dictionary mapping class indices to RGB colors.
        image_size (tuple[int, int]): Size of the images to preprocess.

    Returns:
        None.
    """
    # Get testing folder
    input_images_testing_dir = os.path.join(input_organized_dir, Files.DATASET_TESTING, Files.DATASET_IMAGES)

    # Get some random images
    filenames = os.listdir(input_images_testing_dir)
    random_filenames = random.sample(filenames, Yolo.NUMBER_RANDOM_IMAGES)

    for random_filename in random_filenames:
        # Get the image path
        input_image_path = os.path.join(input_images_testing_dir, random_filename)
        print(f'Testing {input_image_path}')

        # Get the image
        original_image, preprocessed_image = Preprocessing.preprocess(input_image_path, image_size)

        # Run inference
        input_data = run_inference_fn(model, preprocessed_image)

        # Print the detections
        image_bounding_boxes = ImageBoundingBoxes.from_pt_cpu(input_data)
        print(image_bounding_boxes)

        # Display the image with the detections
        Detections.display_detections(model_class_names, preprocessed_image, image_bounding_boxes,
                                      draw_labels_name=draw_labels_name, rgb_colors=rgb_colors)


def test_random_images_pt(input_model_path: str, output_organized_dir: str, colors: dict[int, tuple[int, int, int]],
                          image_size: tuple[int, int] = Preprocessing.SIZE):
    """
    Test random images from the given directory using the given PyTorch model.

    Args:
        input_model_path (str): Path to the PyTorch model file.
        output_organized_dir (str): Directory containing organized dataset images.
        colors (dict[int, tuple[int, int, int]]): Dictionary mapping class indices to RGB colors.
        image_size (tuple[int, int]): Size of the images to preprocess.

    Returns:
        None.
    """
    model = Yolo.load(input_model_path)
    model_class_names = Yolo.get_class_names(model)
    test_random_images(model, model_class_names, Yolo.run_inference, output_organized_dir, False, colors,
                       image_size=image_size)


def main() -> None:
    """
    Main function to run the script.
    """
    parser = argparse.ArgumentParser(description='Script to test YOLO model with a given format')
    Args.add_yolo_input_model_argument(parser)
    Args.add_yolo_format_argument(parser)
    Args.add_yolo_version_argument(parser)
    args = Args.parse_args_as_dict(parser)

    # Get the YOLO input model
    arg_yolo_input_model = Args.get_attribute_from_args(args, Args.INPUT_MODEL)

    # Get the YOLO format
    arg_yolo_format = Args.get_attribute_from_args(args, Args.FORMAT)

    # Get the YOLO version
    arg_yolo_version = Args.get_attribute_from_args(args, Args.VERSION)

    # Get the required dataset folder name
    organized_dir = Files.get_dataset_model_dir_path(Files.DATASET_ORGANIZED, None, arg_yolo_input_model)

    # Get the dataset paths
    weights_best_pt = Files.get_model_best_pt_path(arg_yolo_input_model, arg_yolo_version)

    # Get the class colors
    yolo_colors = None
    if arg_yolo_input_model == Yolo.MODEL_GR:
        if arg_yolo_format == Yolo.FORMAT_PT:
            yolo_colors = Yolo.MODEL_GR_COLORS

    elif arg_yolo_input_model == Yolo.MODEL_GMR:
        if arg_yolo_format == Yolo.FORMAT_PT:
            yolo_colors = Yolo.MODEL_GMR_COLORS

    elif arg_yolo_input_model == Yolo.MODEL_BGOR:
        if arg_yolo_format == Yolo.FORMAT_PT:
            yolo_colors = Yolo.MODEL_BGOR_COLORS

    test_random_images_pt(weights_best_pt, organized_dir, yolo_colors)


if __name__ == '__main__':
    main()
