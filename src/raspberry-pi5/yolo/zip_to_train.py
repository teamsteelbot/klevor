import argparse
import os
import zipfile

from typing_extensions import LiteralString

from files.zip import zip_nested_folder, zip_not_nested_folder
from yolo import (CWD, YOLO_ZIP, ARGS_YOLO_MODEL, YOLO_DATASET_ORGANIZED, YOLO_DATASET_TO_PROCESS, YOLO_DIR,
                  ARGS_YOLO_VERSION, ARGS_YOLO_IS_RETRAINING)
from yolo.args import add_yolo_model_argument, add_yolo_version_argument, add_yolo_is_retraining_argument
from yolo.files import (get_dataset_model_dir_path, get_model_weight_dir_path, get_yolo_notebooks_dir_path,
                        get_yolo_data_dir_path, get_yolo_zip_dir_path, get_yolo_version_dir_path)


# Define the function to zip the required files for model training
def zip_to_train(input_dir: LiteralString, input_yolo_dir: LiteralString, input_yolo_dataset_organized_to_process_dir: LiteralString,
                 input_yolo_version_dir: LiteralString, input_yolo_data_dir: LiteralString, input_yolo_notebooks_dir: LiteralString, input_yolo_weights_dir: LiteralString, output_zip_dir: LiteralString,
                 model_name: str, is_retraining: bool):
    # Define the output zip filename
    output_zip_filename = model_name + '_to_train.zip'
    output_zip_path = os.path.join(output_zip_dir, output_zip_filename)

    # Check if the folder exists, if not create it
    if not os.path.exists(output_zip_dir):
        os.makedirs(output_zip_dir)
        print(f'Created directory: {output_zip_dir}')

    with (zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf):
        # Zip the folders except the YOLO folder
        zip_nested_folder(zipf, input_dir, input_dir, ['yolo', '.git', '.venv', '.idea'])
        print('Zip the folders except the YOLO folder')

        # Zip the YOLO folder files  except its nested folders
        zip_not_nested_folder(zipf, input_dir, input_yolo_dir)
        print('Zip the YOLO folder files except its nested folders')

        # Zip the YOLO version folder except its nested folders
        zip_not_nested_folder(zipf, input_dir, input_yolo_version_dir)
        print('Zip the YOLO version folder except its nested folders')

        # Zip the YOLO dataset organized files
        zip_nested_folder(zipf, input_dir, input_yolo_dataset_organized_to_process_dir)
        print('Zip the YOLO dataset organized files')

        # Zip the YOLO data folder
        zip_nested_folder(zipf, input_dir, input_yolo_data_dir)
        print('Zip the YOLO data folder')

        # Zip the YOLO notebooks folder
        zip_nested_folder(zipf, input_dir, input_yolo_notebooks_dir)
        print('Zip the YOLO notebooks folder')

        # Check if the model is retraining
        if is_retraining:
            # Zip the YOLO model weights folder
            zip_not_nested_folder(zipf, input_dir, input_yolo_weights_dir)
            print('Zip the YOLO model weights folder')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to zip files for YOLO model training')
    add_yolo_model_argument(parser)
    add_yolo_version_argument(parser)
    add_yolo_is_retraining_argument(parser)
    args = parser.parse_args()

    # Get the YOLO model
    arg_yolo_model = getattr(args, ARGS_YOLO_MODEL)

    # Get the YOLO version
    arg_yolo_version = getattr(args, ARGS_YOLO_VERSION)

    # Get the YOLO is retraining
    arg_yolo_is_retraining = getattr(args, ARGS_YOLO_IS_RETRAINING)

    # Get the dataset paths
    organized_to_process_dir = get_dataset_model_dir_path(YOLO_DATASET_ORGANIZED, YOLO_DATASET_TO_PROCESS, arg_yolo_model)

    # Get the YOLO version folder
    yolo_version_dir = get_yolo_version_dir_path(arg_yolo_version)

    # Get the YOLO zip folder
    yolo_zip_dir = get_yolo_zip_dir_path(arg_yolo_version)

    # Get the YOLO model weights folder
    yolo_weights_dir = get_model_weight_dir_path(arg_yolo_model, arg_yolo_version)

    # Get the YOLO data folder
    yolo_data_dir = get_yolo_data_dir_path()

    # Get the YOLO notebooks folder
    yolo_notebooks_dir = get_yolo_notebooks_dir_path(arg_yolo_version)

    # Zip files
    zip_to_train(CWD, YOLO_DIR, organized_to_process_dir, yolo_version_dir, yolo_data_dir, yolo_notebooks_dir, yolo_weights_dir, yolo_zip_dir, arg_yolo_model, arg_yolo_is_retraining)
