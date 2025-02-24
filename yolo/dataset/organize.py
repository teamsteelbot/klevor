import os
import shutil
import random
import opencv.constants as const
import files.files as files

# Directory names
TRAINING = 'train'
VALIDATIONS = 'val'
TESTING = 'test'

# Split the processed into processed, validation, and testing sets
def split_data(input_to_process_dir: str, output_organized_dir: str, output_processed_dir: str = None, train_ratio=0.7,
               val_ratio=0.2):
    input_to_process_images_dir = os.path.join(input_to_process_dir, const.IMAGES)
    input_to_process_annotations_dir = os.path.join(input_to_process_dir, const.LABELS)
    output_processed_images_dir = os.path.join(output_processed_dir, const.IMAGES)
    output_processed_annotations_dir = os.path.join(output_processed_dir, const.LABELS)
    output_organized_training_dir = os.path.join(output_organized_dir, TRAINING)
    output_organized_validations_dir = os.path.join(output_organized_dir, VALIDATIONS)
    output_organized_testing_dir = os.path.join(output_organized_dir, TESTING)
    output_organized_training_images_dir = os.path.join(output_organized_training_dir, const.IMAGES)
    output_organized_validations_images_dir = os.path.join(output_organized_validations_dir, const.IMAGES)
    output_organized_testing_images_dir = os.path.join(output_organized_testing_dir, const.IMAGES)
    output_organized_training_annotations_dir = os.path.join(output_organized_training_dir, const.LABELS)
    output_organized_validations_annotations_dir = os.path.join(output_organized_validations_dir, const.LABELS)
    output_organized_testing_annotations_dir = os.path.join(output_organized_testing_dir, const.LABELS)

    # Check if the path exists, if not it creates it
    for io_dir in [input_to_process_dir, input_to_process_images_dir, input_to_process_annotations_dir,
                   output_processed_dir, output_processed_images_dir, output_processed_annotations_dir,
                   output_organized_dir, output_organized_training_dir, output_organized_validations_dir,
                   output_organized_testing_dir, output_organized_training_images_dir,
                   output_organized_validations_images_dir, output_organized_testing_images_dir,
                   output_organized_training_annotations_dir, output_organized_validations_annotations_dir,
                   output_organized_testing_annotations_dir]:
        if io_dir is not None and not os.path.exists(io_dir):
            os.makedirs(io_dir)

    # Define the class file and notes image_filename
    classes_file = os.path.join(input_to_process_dir, const.CLASSES)
    notes_file = os.path.join(input_to_process_dir, const.NOTES)

    # Copy the class file and notes file
    files.copy_file(classes_file, os.path.join(output_organized_dir, const.CLASSES))
    files.copy_file(notes_file, os.path.join(output_organized_dir, const.NOTES))

    # Get the list of files
    image_filenames = os.listdir(input_to_process_images_dir)
    random.shuffle(image_filenames)

    # Split the processed
    train_split = int(len(image_filenames) * train_ratio)
    val_split = int(len(image_filenames) * val_ratio)

    # Copy the files to the output directories
    for i, image_filename in enumerate(image_filenames):
        # Get the image and annotations paths
        input_to_process_image_path = os.path.join(input_to_process_images_dir, image_filename)
        annotations_filename = os.path.splitext(image_filename)[0] + '.txt'
        input_to_process_annotations_path = os.path.join(input_to_process_annotations_dir, annotations_filename)

        if i < train_split:
            files.copy_file(input_to_process_image_path, output_organized_training_images_dir)
            files.copy_file(input_to_process_annotations_path, output_organized_training_annotations_dir)
        elif i < train_split + val_split:
            files.copy_file(input_to_process_image_path, output_organized_validations_images_dir)
            files.copy_file(input_to_process_annotations_path, output_organized_validations_annotations_dir)
        else:
            files.copy_file(input_to_process_image_path, output_organized_testing_images_dir)
            files.copy_file(input_to_process_annotations_path, output_organized_testing_annotations_dir)

        # Move the files to the processed directory
        if output_processed_dir is not None:
            files.move_file(input_to_process_image_path, os.path.join(output_processed_images_dir, image_filename))
            files.move_file(input_to_process_annotations_path,
                            os.path.join(output_processed_annotations_dir, annotations_filename))

        # Log
        print(f'Copied {image_filename} to the respective directories')

    if output_processed_dir is not None:
        # Move the class file and notes file to the processed directory
        files.move_file(classes_file, output_processed_dir)
        files.move_file(notes_file, output_processed_dir)


if __name__ == '__main__':
    # Set the input and output directories
    cwd = os.getcwd()
    base_dir = os.path.join(cwd, 'yolo', 'dataset')
    input_to_process_dir = os.path.join(base_dir, 'augmented', 'to_process')
    output_organized_dir = os.path.join(base_dir, 'organized', 'to_process')
    output_processed_dir = os.path.join(base_dir, 'augmented', 'processed')

    split_data(input_to_process_dir, output_organized_dir, output_processed_dir)
