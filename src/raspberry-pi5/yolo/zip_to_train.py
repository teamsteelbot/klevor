import argparse
import os
import zipfile

from typing_extensions import LiteralString

from args import get_attribute_from_args, parse_args_as_dict
from files import ensure_path_exists
from files.zip import zip_nested_folder, zip_not_nested_folder
from yolo import (CWD, ARGS_YOLO_INPUT_MODEL, YOLO_DATASET_ORGANIZED, YOLO_DIR,
                  ARGS_YOLO_VERSION, ARGS_YOLO_RETRAINING, ZIP_IGNORE_DIR)
from yolo.args import add_yolo_input_model_argument, add_yolo_version_argument, add_yolo_retraining_argument
from yolo.files import (get_dataset_model_dir_path, get_model_weight_dir_path,
                        get_yolo_data_dir_path, get_yolo_zip_dir_path, get_yolo_version_dir_path)


# Define the function to zip the required files for model training
def zip_to_train(input_dir: LiteralString, input_yolo_dir: LiteralString, input_yolo_dataset_organized_dir: LiteralString,
                 input_yolo_version_dir: LiteralString, input_yolo_data_dir: LiteralString, input_yolo_weights_dir: LiteralString, output_zip_dir: LiteralString,
                 model_name: str, retraining: str):
    # Define the output zip filename
    output_zip_filename = model_name + '_to_train.zip'
    output_zip_path = os.path.join(output_zip_dir, output_zip_filename)

    # Check if the folder exists, if not create it
    ensure_path_exists(output_zip_dir)

    with (zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf):
        # Zip the folders except the YOLO folder
        zip_nested_folder(zipf, input_dir, input_dir, ZIP_IGNORE_DIR)
        print('Zip the folders except the YOLO folder')

        # Zip the YOLO folder files  except its nested folders
        zip_not_nested_folder(zipf, input_dir, input_yolo_dir)
        print('Zip the YOLO folder files except its nested folders')

        # Zip the YOLO version folder except its nested folders
        zip_not_nested_folder(zipf, input_dir, input_yolo_version_dir)
        print('Zip the YOLO version folder except its nested folders')

        # Zip the YOLO dataset organized files
        zip_nested_folder(zipf, input_dir, input_yolo_dataset_organized_dir)
        print('Zip the YOLO dataset organized files')

        # Zip the YOLO data folder
        zip_nested_folder(zipf, input_dir, input_yolo_data_dir)
        print('Zip the YOLO data folder')

        # Check if the model is retraining
        if retraining:
            # Zip the YOLO model weights folder
            zip_not_nested_folder(zipf, input_dir, input_yolo_weights_dir)
            print('Zip the YOLO model weights folder')

# Main function to run the script
def main() -> None:
    parser = argparse.ArgumentParser(description='Script to zip files for YOLO model training')
    add_yolo_input_model_argument(parser)
    add_yolo_version_argument(parser)
    add_yolo_retraining_argument(parser)
    args = parse_args_as_dict(parser)

    # Get the YOLO input model
    arg_yolo_input_model = get_attribute_from_args(args, ARGS_YOLO_INPUT_MODEL)

    # Get the YOLO version
    arg_yolo_version = get_attribute_from_args(args, ARGS_YOLO_VERSION)

    # Get the YOLO retraining
    arg_yolo_retraining = get_attribute_from_args(args, ARGS_YOLO_RETRAINING)

    # Get the dataset paths
    organized_dir = get_dataset_model_dir_path(YOLO_DATASET_ORGANIZED, None, arg_yolo_input_model)

    # Get the YOLO version folder
    yolo_version_dir = get_yolo_version_dir_path(arg_yolo_version)

    # Get the YOLO zip folder
    yolo_zip_dir = get_yolo_zip_dir_path(arg_yolo_version)

    # Get the YOLO model weights folder
    yolo_weights_dir = get_model_weight_dir_path(arg_yolo_input_model, arg_yolo_version)

    # Get the YOLO data folder
    yolo_data_dir = get_yolo_data_dir_path()

    # Zip files
    zip_to_train(CWD, YOLO_DIR, organized_dir, yolo_version_dir, yolo_data_dir, yolo_weights_dir, yolo_zip_dir,
                 arg_yolo_input_model, arg_yolo_retraining)


if __name__ == '__main__':
    main()