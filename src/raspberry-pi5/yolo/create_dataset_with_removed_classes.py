import argparse
import json
import os
import shutil

from args import get_attribute_from_args, parse_args_as_dict
from files import ensure_path_exists
from yolo import (ARGS_YOLO_INPUT_MODEL, YOLO_DATASET_LABELED, ARGS_YOLO_OUTPUT_MODEL, ARGS_YOLO_IGNORE_CLASSES,
                  YOLO_DATASET_LABELS, YOLO_DATASET_IMAGES, YOLO_DATASET_IMAGES_EXT, YOLO_DATASET_CLASSES_TXT,
                  YOLO_DATASET_NOTES_JSON, YOLO_DATASET_TO_PROCESS)
from yolo.args import add_yolo_input_model_argument, add_yolo_output_model_argument, add_yolo_ignore_classes_argument
from yolo.files import get_dataset_model_dir_path


# Create a new dataset with the labeled classes removed
def create_dataset_with_removed_classes(input_dir, input_to_process_dir, output_dir, output_to_process_dir, ignore_classes):
    # Create the output directory if it doesn't exist
    ensure_path_exists(output_dir)

    # Get the input directory for images and labels
    input_annotations_dir = os.path.join(input_to_process_dir, YOLO_DATASET_LABELS)
    input_images_dir = os.path.join(input_to_process_dir, YOLO_DATASET_IMAGES)

    # Get the input classes and notes file paths
    input_classes_path = os.path.join(input_dir, YOLO_DATASET_CLASSES_TXT)
    input_notes_path = os.path.join(input_dir, YOLO_DATASET_NOTES_JSON)

    # Create the output directories for images and labels
    output_annotations_dir = os.path.join(output_to_process_dir, YOLO_DATASET_LABELS)
    output_images_dir = os.path.join(output_to_process_dir, YOLO_DATASET_IMAGES)

    for dir_path in [output_annotations_dir, output_images_dir]:
        ensure_path_exists(dir_path)

    # Get the output classes and notes file paths
    output_classes_path = os.path.join(output_dir, YOLO_DATASET_CLASSES_TXT)
    output_notes_path = os.path.join(output_dir, YOLO_DATASET_NOTES_JSON)

    # Get the indexes of the classes to ignore from the classes file
    ignore_classes_indexes = []
    classes_indexes = {}
    class_counter = 0
    new_classes = []
    with open(input_classes_path, 'r') as f:
        # Read the classes from the file
        classes = f.readlines()

        # Remove empty lines and strip whitespace
        classes = [cls.strip() for cls in classes if cls.strip()]

        # Iterate through the classes and find the indexes of the classes to ignore
        for idx, cls in enumerate(classes):
            ignore_cls=False
            if cls in ignore_classes:
                ignore_classes_indexes.append(idx)
                ignore_cls=True

            if not ignore_cls:
                new_classes.append(cls)
                classes_indexes[idx] = class_counter
                class_counter += 1

    # Check if all the ignored classes are present in the classes file
    if len(ignore_classes_indexes) != len(ignore_classes):
        raise RuntimeError(f"Warning: Not all ignored classes are present in the classes file. Ignored classes: {ignore_classes}, Found indexes: {ignore_classes_indexes}")

    # Write the new classes to the output classes file
    with open(output_classes_path, 'w') as f:
        for cls in new_classes:
            f.write(cls + '\n')
    print(f"Copied {input_classes_path} to {output_classes_path}")

    # Remove the ignored classes from the notes file
    with open(input_notes_path, 'r') as f:
        new_notes_json_data = json.load(f)

        # Get the categories from the JSON data
        categories = new_notes_json_data.get('categories', [])

        # Filter out the ignored classes
        filtered_categories = [cat for cat in categories if cat['id'] not in ignore_classes_indexes]

        # Update the IDs of the remaining categories
        for i, cat in enumerate(filtered_categories):
            cat['id'] = classes_indexes.get(cat['id'])
            cat['name'] = new_classes[i]

        # Update the JSON data with the filtered categories
        new_notes_json_data['categories'] = filtered_categories

    # Write the updated JSON data to the output notes file
    with open(output_notes_path, 'w') as f:
        json.dump(new_notes_json_data, f, indent=4)
    print(f"Copied {input_notes_path} to {output_notes_path}")

    # Iterate through the images and labels in the input directory
    for input_label_name in os.listdir(input_annotations_dir):
        # Get the input label path
        input_label_path = os.path.join(input_annotations_dir, input_label_name)

        # Get the input image name and path
        input_image_name = input_label_name.replace(".txt", YOLO_DATASET_IMAGES_EXT)
        input_image_path = os.path.join(input_images_dir, input_image_name)
        if not os.path.exists(input_image_path):
            print(f"Image file {input_image_path} does not exist. Skipping...")
            continue

        # Copy the image file to the output directory
        output_image_path = os.path.join(output_images_dir, input_image_name)
        shutil.copy(input_image_path, output_image_path)
        print(f"Copied {input_image_path} to {output_image_path}")

        # Read the label file and filter out the ignored classes
        with open(input_label_path, 'r') as f:
            lines = f.readlines()

        # Write the filtered labels to the output label file
        output_label_path = os.path.join(output_annotations_dir, input_label_name)
        with open(output_label_path, 'w') as f:
            for line in lines:
                line_parts = line.split()
                class_id = int(line_parts[0])
                if class_id not in ignore_classes_indexes:
                    line_parts[0] = str(classes_indexes.get(class_id))
                    f.write(" ".join(line_parts) + '\n')
        print(f"Copied {input_label_path} to {output_label_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to remove labeled classes from a given YOLO model dataset')
    add_yolo_input_model_argument(parser)
    add_yolo_output_model_argument(parser)
    add_yolo_ignore_classes_argument(parser)
    args = parse_args_as_dict(parser)

    # Get the YOLO input model
    arg_yolo_input_model = get_attribute_from_args(args, ARGS_YOLO_INPUT_MODEL)

    # Get the YOLO output model
    arg_yolo_output_model = get_attribute_from_args(args, ARGS_YOLO_OUTPUT_MODEL)

    # Get the YOLO ignore classes
    arg_yolo_ignore_classes = get_attribute_from_args(args, ARGS_YOLO_IGNORE_CLASSES)

    # Get the dataset paths
    input_labeled_dir = get_dataset_model_dir_path(YOLO_DATASET_LABELED, None, arg_yolo_input_model)
    input_labeled_to_process_dir = get_dataset_model_dir_path(YOLO_DATASET_LABELED, YOLO_DATASET_TO_PROCESS, arg_yolo_input_model)
    output_labeled_dir = get_dataset_model_dir_path(YOLO_DATASET_LABELED, None, arg_yolo_output_model)
    output_labeled_to_process_dir = get_dataset_model_dir_path(YOLO_DATASET_LABELED, YOLO_DATASET_TO_PROCESS, arg_yolo_output_model)

    # Create the dataset with removed classes
    create_dataset_with_removed_classes(input_labeled_dir, input_labeled_to_process_dir, output_labeled_dir, output_labeled_to_process_dir, arg_yolo_ignore_classes)