import os
import re
import time
import zipfile

from files import IGNORE_DIRS, ensure_path_exists, BATCH_SIZE, ENVIRONMENT_LOCAL, ENVIRONMENT_COLAB, \
    GOOGLE_DRIVE_API_CALL_DELAY


def match_any(regex_list: list[re.Pattern], string: str):
    """
    Match any regex pattern in a list.
    """
    return any(regex.match(string) for regex in regex_list)


def zip_files(zipf, filenames, input_file_base_path: str, input_base_path: str,
              ignore_filenames_regex: list[re.Pattern] = None):
    """
    Define the function to zip the files in a folder.
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

def zip_not_nested_folder(zipf, input_base_path: str, input_folder_path: str, ignore_filenames_regex: list = None):
    """
    Define the function to zip a folder, this ignores nested folders.
    """
    # Get the list of files in the specified folder
    filenames = [f for f in os.listdir(input_folder_path)]

    # Zip the files in the folder
    zip_files(zipf, filenames, input_folder_path, input_base_path, ignore_filenames_regex)

    # Log
    input_folder_rel_path = os.path.relpath(input_folder_path, input_base_path)
    print(f'Zipped folder: {input_folder_rel_path}')

def zip_nested_folder(zipf, input_base_path: str, input_folder_path: str, ignore_dirs: list[str] = None,
                      ignore_filenames_regex: list[re.Pattern] = None):
    """
    Define the function to zip a folder, this includes nested folders.
    """
    # Added to ignore directories the list of directories that should be always ignored
    if ignore_dirs is None:
        ignore_dirs = []
    ignore_dirs += IGNORE_DIRS

    for root, _, filenames in os.walk(input_folder_path):
        # Skip directories in the ignore list
        filenames = [f for f in filenames if not any(os.path.relpath(root, input_base_path).startswith(d) for d in ignore_dirs)]

        # Zip the files in the subfolders
        zip_files(zipf, filenames, root, input_base_path, ignore_filenames_regex)

    # Log
    input_folder_rel_path = os.path.relpath(input_folder_path, input_base_path)
    print(f'Zipped folder: {input_folder_rel_path}')

def extract_all(zip_path, output_dir, environment=ENVIRONMENT_LOCAL, batch_size=BATCH_SIZE):
    """
    Extract all files from a zip file by batches.
    """
    # Check if the path exists, if not it creates it
    ensure_path_exists(output_dir)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        files = zip_ref.namelist()
    
        for i in range(0, len(files), batch_size):
            # Extract a batch of files
            batch_files = files[i:i + batch_size]
    
            for file in batch_files:
                print(f"Extracting {file}...")

                # Extract the file to the output directory
                file_path = os.path.join(output_dir, file)
                ensure_path_exists(file_path)
                zip_ref.extract(file, output_dir)

                if environment == ENVIRONMENT_LOCAL:
                    continue

                # Sleep to avoid Google Drive API call limit
                if environment == ENVIRONMENT_COLAB:
                    time.sleep(GOOGLE_DRIVE_API_CALL_DELAY)