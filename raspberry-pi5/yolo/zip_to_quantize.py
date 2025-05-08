import argparse
import os
import zipfile

from args.args import get_attribute_name
from files.zip import zip_nested_folder, zip_not_nested_folder
from model.model_yolo import get_model_name
from yolo import (ARGS_YOLO_MODEL, CWD, YOLO_RUNS, YOLO_ZIP, YOLO_DIR)
from yolo.args import add_yolo_model_argument


# Define the function to zip the required files for model quantization
def zip_to_quantize(input_dir: str, input_yolo_dir: str, input_yolo_runs_dir: str, output_zip_dir: str,
                    model_name: str):
    # Define the output zip filename
    output_zip_filename = model_name + '_to_quantize.zip'
    output_zip_path = os.path.join(output_zip_dir, output_zip_filename)

    with (zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf):
        # Zip the folders except the YOLO folder
        zip_nested_folder(zipf, input_dir, input_dir, ['yolo', '.git', '.venv', '.idea'])
        print('Zip the folders except the YOLO folder')

        # Zip the YOLO folder files except the dataset, runs and zip folders
        zip_not_nested_folder(zipf, input_dir, input_yolo_dir)
        print('Zip the YOLO folder files except the dataset, runs and zip folders')

        # Zip the YOLO dataset organized files
        zip_nested_folder(zipf, input_dir, os.path.join(input_yolo_runs_dir, model_name))
        print('Zip the YOLO model runs folder')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to zip files for YOLO model quantization')
    add_yolo_model_argument(parser)
    args = parser.parse_args()

    # Get the YOLO model
    arg_yolo_model = getattr(args, get_attribute_name(ARGS_YOLO_MODEL))

    # Get the YOLO model name
    model_name = get_model_name(arg_yolo_model)

    # Zip files
    zip_to_quantize(CWD, YOLO_DIR, YOLO_RUNS, YOLO_ZIP, model_name)
