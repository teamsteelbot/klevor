import argparse
import os
import zipfile
from typing import LiteralString

from files.zip import Zip
from yolo.args import Args
from yolo.files import Files


def zip_to_quantize(input_dir: LiteralString, input_yolo_dir: LiteralString, input_yolo_runs_dir: LiteralString,
                    input_yolo_version_dir: LiteralString, output_zip_dir: LiteralString,
                    model_name: str) -> None:
    """
    Define the function to zip the required files for model quantization

    Args:
        input_dir (str): The input directory containing the YOLO files.
        input_yolo_dir (str): The YOLO directory.
        input_yolo_runs_dir (str): The YOLO runs directory.
        input_yolo_version_dir (str): The YOLO version directory.
        output_zip_dir (str): The output directory where the zip file will be saved.
        model_name (str): The name of the model to be used in the zip file name.

    Returns:
        None
    """
    # Define the output zip filename
    output_zip_filename = model_name + '_to_quantize.zip'
    output_zip_path = os.path.join(output_zip_dir, output_zip_filename)

    # Check if the folder exists, if not create it
    Files.ensure_path_exists(output_zip_dir)

    with (zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf):
        # Zip the folders except the YOLO folder
        Zip.zip_nested_folder(zipf, input_dir, input_dir, Files.ZIP_IGNORE)
        print('Zip the folders except the YOLO folder')

        # Zip the YOLO folder files except its nested folders
        Zip.zip_not_nested_folder(zipf, input_dir, input_yolo_dir)
        print('Zip the YOLO folder files except its nested folders')

        # Zip the YOLO version folder except its nested folders
        Zip.zip_not_nested_folder(zipf, input_dir, input_yolo_version_dir)
        print('Zip the YOLO version folder except its nested folders')

        # Zip the YOLO model runs folder
        Zip.zip_nested_folder(zipf, input_dir, input_yolo_runs_dir)
        print('Zip the YOLO model runs folder')


def main() -> None:
    """
    Main function to run the script.
    """
    parser = argparse.ArgumentParser(description='Script to zip files for YOLO model quantization')
    Args.add_yolo_input_model_argument(parser)
    Args.add_yolo_version_argument(parser)
    args = Args.parse_args_as_dict(parser)

    # Get the YOLO input model
    arg_yolo_input_model = Args.get_attribute_from_args(args, Args.INPUT_MODEL)

    # Get the YOLO version
    arg_yolo_version = Args.get_attribute_from_args(args, Args.VERSION)

    # Get the YOLO version folder
    yolo_version_dir = Files.get_yolo_version_dir_path(arg_yolo_version)

    # Get the YOLO runs folder
    yolo_runs_dir = Files.get_yolo_runs_dir_path(arg_yolo_version)

    # Get the YOLO zip folder
    yolo_zip_dir = Files.get_yolo_zip_dir_path(arg_yolo_version)

    # Zip files
    zip_to_quantize(Files.CWD, Files.YOLO_DIR, yolo_runs_dir, yolo_version_dir, yolo_zip_dir, arg_yolo_input_model)


if __name__ == '__main__':
    main()
