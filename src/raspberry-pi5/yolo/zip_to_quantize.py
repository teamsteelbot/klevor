import argparse
import os
import zipfile
from typing import LiteralString

from files.zip import zip_nested_folder, zip_not_nested_folder
from yolo import (ARGS_YOLO_MODEL, CWD, YOLO_DIR,
                  ARGS_YOLO_VERSION)
from yolo.args import add_yolo_model_argument, add_yolo_version_argument
from yolo.files import (get_yolo_zip_dir_path, get_yolo_runs_dir_path,
                        get_yolo_version_dir_path, get_yolo_notebooks_dir_path)


# Define the function to zip the required files for model quantization
def zip_to_quantize(input_dir: LiteralString, input_yolo_dir: LiteralString, input_yolo_runs_dir: LiteralString, input_yolo_version_dir: LiteralString, input_yolo_notebooks_dir: LiteralString, output_zip_dir: LiteralString,
                    model_name: str):
    # Define the output zip filename
    output_zip_filename = model_name + '_to_quantize.zip'
    output_zip_path = os.path.join(output_zip_dir, output_zip_filename)

    # Check if the folder exists, if not create it
    if not os.path.exists(output_zip_dir):
        os.makedirs(output_zip_dir)
        print(f'Created directory: {output_zip_dir}')

    with (zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf):
        # Zip the folders except the YOLO folder
        zip_nested_folder(zipf, input_dir, input_dir, ['yolo', '.git', '.venv', '.idea'])
        print('Zip the folders except the YOLO folder')

        # Zip the YOLO folder files except its nested folders
        zip_not_nested_folder(zipf, input_dir, input_yolo_dir)
        print('Zip the YOLO folder files except its nested folders')

        # Zip the YOLO version folder except its nested folders
        zip_not_nested_folder(zipf, input_dir, input_yolo_version_dir)
        print('Zip the YOLO version folder except its nested folders')

        # Zip the YOLO notebooks folder
        zip_nested_folder(zipf, input_dir, input_yolo_notebooks_dir)
        print('Zip the YOLO version colab folder')

        # Zip the YOLO model runs folder
        zip_nested_folder(zipf, input_dir, input_yolo_runs_dir)
        print('Zip the YOLO model runs folder')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to zip files for YOLO model quantization')
    add_yolo_model_argument(parser)
    add_yolo_version_argument(parser)
    args = parser.parse_args()

    # Get the YOLO model
    arg_yolo_model = getattr(args, ARGS_YOLO_MODEL)

    # Get the YOLO version
    arg_yolo_version = getattr(args, ARGS_YOLO_VERSION)

    # Get the YOLO version folder
    yolo_version_dir = get_yolo_version_dir_path(arg_yolo_version)

    # Get the YOLO runs folder
    yolo_runs_dir = get_yolo_runs_dir_path(arg_yolo_version)

    # Get the YOLO zip folder
    yolo_zip_dir = get_yolo_zip_dir_path(arg_yolo_version)

    # Get the YOLO notebooks folder
    yolo_notebooks_dir = get_yolo_notebooks_dir_path(arg_yolo_version)

    # Zip files
    zip_to_quantize(CWD, YOLO_DIR, yolo_runs_dir, yolo_version_dir, yolo_notebooks_dir, yolo_zip_dir, arg_yolo_model)
