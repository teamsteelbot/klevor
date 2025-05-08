import argparse
import os
import zipfile

from typing_extensions import LiteralString

from args.args import get_attribute_name
from files.zip import zip_nested_folder, zip_not_nested_folder
from model.model_yolo import get_dataset_model_name, get_model_name
from yolo import (CWD, YOLO_ZIP, ARGS_YOLO_MODEL, YOLO_MODEL_2C, YOLO_MODEL_4C, YOLO_DATASET_ORGANIZED, YOLO_TO_PROCESS,
                  YOLO_DATASET, YOLO_DIR)
from yolo.args import add_yolo_model_argument


# Define the function to zip the required files for model training
def zip_to_train(input_dir: LiteralString, input_yolo_dir: LiteralString, input_yolo_dataset_organized_to_process_dir: LiteralString,
                 output_zip_dir: LiteralString,
                 model_name: str):
    # Define the output zip filename
    output_zip_filename = model_name + '_to_train.zip'
    output_zip_path = os.path.join(output_zip_dir, output_zip_filename)

    with (zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf):
        # Zip the folders except the YOLO folder
        zip_nested_folder(zipf, input_dir, input_dir, ['yolo', '.git', '.venv', '.idea'])
        print('Zip the folders except the YOLO folder')

        # Zip the YOLO folder files except the dataset, runs and zip folders
        zip_not_nested_folder(zipf, input_dir, input_yolo_dir)
        print('Zip the YOLO folder files except the dataset, runs and zip folders')

        # Zip the YOLO dataset organized files
        zip_nested_folder(zipf, input_dir, input_yolo_dataset_organized_to_process_dir)
        print('Zip the YOLO dataset organized files')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to zip files for YOLO model training')
    add_yolo_model_argument(parser)
    args = parser.parse_args()

    # Get the YOLO model
    arg_yolo_model = getattr(args, get_attribute_name(ARGS_YOLO_MODEL))

    # Get the YOLO model name
    model_name = get_model_name(arg_yolo_model)

    # Get the required dataset folder name
    organized_dataset_name = get_dataset_model_name(YOLO_DATASET_ORGANIZED, arg_yolo_model)

    # Get the dataset paths
    yolo_dataset_organized_to_process = os.path.join(YOLO_DATASET, organized_dataset_name, YOLO_TO_PROCESS)

    # Zip files

    zip_to_train(CWD, YOLO_DIR, yolo_dataset_organized_to_process, YOLO_ZIP, model_name)
