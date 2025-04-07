import argparse
import os
import zipfile
from files.zip import zip_nested_folder, zip_not_nested_folder
from yolo import (CWD, YOLO, YOLO_DATASET_ORGANIZED_2C_TO_PROCESS, YOLO_2C_NAME,
                  YOLO_DATASET_ORGANIZED_4C_TO_PROCESS, YOLO_ZIP, YOLO_4C_NAME, ARGS_YOLO_MODEL_2C,
                  ARGS_YOLO_MODEL, ARGS_YOLO_MODEL_4C, ARGS_YOLO_MODEL_PROP)


# Define the function to zip the required files for model training
def zip_to_train(input_dir: str, input_yolo_dir: str, input_yolo_dataset_organized_to_process_dir: str,
                 output_zip_dir: str,
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
    parser.add_argument(ARGS_YOLO_MODEL, type=str, required=True, help='YOLO model',
                        choices=[ARGS_YOLO_MODEL_2C, ARGS_YOLO_MODEL_4C])
    args = parser.parse_args()

    # Get the YOLO model
    arg_yolo_model = getattr(args, ARGS_YOLO_MODEL_PROP)

    # Zip files
    if arg_yolo_model == ARGS_YOLO_MODEL_2C:
        zip_to_train(CWD, YOLO, YOLO_DATASET_ORGANIZED_2C_TO_PROCESS, YOLO_ZIP, YOLO_2C_NAME)

    else:
        zip_to_train(CWD, YOLO, YOLO_DATASET_ORGANIZED_4C_TO_PROCESS, YOLO_ZIP, YOLO_4C_NAME)
