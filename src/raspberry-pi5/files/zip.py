import os
from re import Pattern
import time
import zipfile

from files import Files
from utils import match_any


class Zip:
    """
    Class for zipping files and folders.
    """

    @staticmethod
    def zip_files(zipf, filenames, input_file_base_path: str, input_base_path: str,
                  ignore_filenames_regex: list[Pattern] = None) -> None:
        """
        Define the function to zip the files in a folder.

        Args:
            zipf: ZipFile object to write to.
            filenames (list): List of filenames to zip.
            input_file_base_path (str): Base path of the files to be zipped.
            input_base_path (str): Base path for relative file paths in the zip.
            ignore_filenames_regex (list[Pattern], optional): List of regex patterns to ignore certain files.
        """
        for filename in filenames:
            # Skip the file if it is in the ignore list
            if ignore_filenames_regex is not None and match_any(ignore_filenames_regex, filename):
                continue

            # Zip the file
            file_path = os.path.join(input_file_base_path, filename)
            file_rel_path = os.path.relpath(file_path, input_base_path)
            zipf.write(file_path, file_rel_path)

            # Log
            print(f'Zipped file: {file_rel_path}')

    @staticmethod
    def zip_not_nested_folder(zipf, input_base_path: str, input_folder_path: str, ignore_filenames_regex: list = None)->None:
        """
        Define the function to zip a folder, this ignores nested folders.

        Args:
            zipf: ZipFile object to write to.
            input_base_path (str): Base path for relative file paths in the zip.
            input_folder_path (str): Path of the folder to be zipped.
            ignore_filenames_regex (list[Pattern], optional): List of regex patterns to ignore certain files.
        """
        # Get the list of files in the specified folder
        filenames = [f for f in os.listdir(input_folder_path)]

        # Zip the files in the folder
        Zip.zip_files(zipf, filenames, input_folder_path, input_base_path, ignore_filenames_regex)

        # Log
        input_folder_rel_path = os.path.relpath(input_folder_path, input_base_path)
        print(f'Zipped folder: {input_folder_rel_path}')

    @staticmethod
    def zip_nested_folder(zipf, input_base_path: str, input_folder_path: str, ignore_dirs: list[str] = None,
                          ignore_filenames_regex: list[Pattern] = None)->None:
        """
        Define the function to zip a folder, this includes nested folders.

        Args:
            zipf: ZipFile object to write to.
            input_base_path (str): Base path for relative file paths in the zip.
            input_folder_path (str): Path of the folder to be zipped.
            ignore_dirs (list[str], optional): List of directories to ignore.
            ignore_filenames_regex (list[Pattern], optional): List of regex patterns to ignore certain files.
        """
        # Added to ignore directories the list of directories that should be always ignored
        if ignore_dirs is None:
            ignore_dirs = []
        ignore_dirs += Files.IGNORE_DIRS

        for root, _, filenames in os.walk(input_folder_path):
            # Skip directories in the ignore list
            filenames = [f for f in filenames if not any(os.path.relpath(root, input_base_path).startswith(d) for d in ignore_dirs)]

            # Zip the files in the subfolders
            Zip.zip_files(zipf, filenames, root, input_base_path, ignore_filenames_regex)

        # Log
        input_folder_rel_path = os.path.relpath(input_folder_path, input_base_path)
        print(f'Zipped folder: {input_folder_rel_path}')

    @staticmethod
    def extract_all(zip_path, output_dir, environment=Files.ENVIRONMENT_LOCAL, batch_size=Files.BATCH_SIZE)->None:
        """
        Extract all files from a zip file by batches.

        Args:
            zip_path (str): Path to the zip file.
            output_dir (str): Directory where files will be extracted.
            environment (str): Environment type, either 'local' or 'colab'.
            batch_size (int): Number of files to extract in each batch.
        """
        # Check if the path exists, if not it creates it
        Files.ensure_path_exists(output_dir)

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            files = zip_ref.namelist()

            for i in range(0, len(files), batch_size):
                # Extract a batch of files
                batch_files = files[i:i + batch_size]

                for file in batch_files:
                    print(f"Extracting {file}...")

                    # Extract the file to the output directory
                    file_path = os.path.join(output_dir, file)
                    Files.ensure_path_exists(file_path)
                    zip_ref.extract(file, output_dir)

                    if environment == Files.ENVIRONMENT_LOCAL:
                        continue

                    # Sleep to avoid Google Drive API call limit
                    if environment == Files.ENVIRONMENT_COLAB:
                        time.sleep(Files.GOOGLE_DRIVE_API_CALL_DELAY)