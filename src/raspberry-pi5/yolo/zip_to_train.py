from argparse import ArgumentParser
import os
import zipfile

from typing_extensions import LiteralString

from files.zip import Zip
from yolo.args import Args
from yolo.files import Files


def zip_to_train(input_dir: LiteralString, input_yolo_dir: LiteralString,
                 input_yolo_dataset_organized_dir: LiteralString,
                 input_yolo_version_dir: LiteralString, input_yolo_data_dir: LiteralString,
                 input_yolo_weights_dir: LiteralString, output_zip_dir: LiteralString,
                 model_name: str, retraining: str) -> None:
    """
    Define the function to zip the required files for model training.

    Args:
        input_dir (str): The base input directory where the YOLO files are located.
        input_yolo_dir (str): The directory containing the YOLO files.
        input_yolo_dataset_organized_dir (str): The directory containing the organized dataset files.
        input_yolo_version_dir (str): The directory for the specific YOLO version.
        input_yolo_data_dir (str): The directory containing the YOLO data files.
        input_yolo_weights_dir (str): The directory containing the YOLO model weights.
        output_zip_dir (str): The directory where the output zip file will be saved.
        model_name (str): The name of the model to be used in the zip filename.
        retraining (bool): Flag indicating if this is a retraining operation.

    Returns:
        None
    """
    # Define the output zip filename
    output_zip_filename = model_name + '_to_train.zip'
    output_zip_path = os.path.join(output_zip_dir, output_zip_filename)

    # Check if the folder exists, if not create it
    Files.ensure_directory_exists(output_zip_dir)

    with (zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf):
        # Zip the folders except the YOLO folder
        Zip.zip_nested_folder(zipf, input_dir, input_dir, Files.ZIP_IGNORE)
        print('Zip the folders except the YOLO folder')

        # Zip the YOLO folder files  except its nested folders
        Zip.zip_not_nested_folder(zipf, input_dir, input_yolo_dir)
        print('Zip the YOLO folder files except its nested folders')

        # Zip the YOLO version folder except its nested folders
        Zip.zip_not_nested_folder(zipf, input_dir, input_yolo_version_dir)
        print('Zip the YOLO version folder except its nested folders')

        # Zip the YOLO dataset organized files
        Zip.zip_nested_folder(zipf, input_dir, input_yolo_dataset_organized_dir)
        print('Zip the YOLO dataset organized files')

        # Zip the YOLO data folder
        Zip.zip_nested_folder(zipf, input_dir, input_yolo_data_dir)
        print('Zip the YOLO data folder')

        # Check if the model is retraining
        if retraining:
            # Zip the YOLO model weights folder
            Zip.zip_not_nested_folder(zipf, input_dir, input_yolo_weights_dir)
            print('Zip the YOLO model weights folder')


def main() -> None:
    """
    Main function to run the script.
    """
    parser = ArgumentParser(description='Script to zip files for YOLO model training')
    Args.add_yolo_input_model_argument(parser)
    Args.add_yolo_version_argument(parser)
    Args.add_yolo_retraining_argument(parser)
    args = Args.parse_args_as_dict(parser)

    # Get the YOLO input model
    arg_yolo_input_model = Args.get_attribute_from_args(args, Args.INPUT_MODEL)

    # Get the YOLO version
    arg_yolo_version = Args.get_attribute_from_args(args, Args.VERSION)

    # Get the YOLO retraining
    arg_yolo_retraining = Args.get_attribute_from_args(args, Args.RETRAINING)

    # Get the dataset paths
    organized_dir = Files.get_dataset_model_dir_path(Files.DATASET_ORGANIZED, None, arg_yolo_input_model)

    # Get the YOLO version folder
    yolo_version_dir = Files.get_yolo_version_dir_path(arg_yolo_version)

    # Get the YOLO zip folder
    yolo_zip_dir = Files.get_yolo_zip_dir_path(arg_yolo_version)

    # Get the YOLO model weights folder
    yolo_weights_dir = Files.get_model_weight_dir_path(arg_yolo_input_model, arg_yolo_version)

    # Get the YOLO data folder
    yolo_data_dir = Files.get_yolo_data_dir_path()

    # Zip files
    zip_to_train(Files.CWD, Files.YOLO_DIR, organized_dir, yolo_version_dir, yolo_data_dir, yolo_weights_dir,
                 yolo_zip_dir, arg_yolo_input_model, arg_yolo_retraining)


if __name__ == '__main__':
    main()
