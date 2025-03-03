import os
import re


# Match any regex pattern in a list
def match_any(regex_list: list[re.Pattern], string: str):
    return any(regex.match(string) for regex in regex_list)


# Define the function to zip the files in a folder
def zip_files(zipf, filenames, input_file_base_path: str, input_base_path: str,
              ignore_filenames_regex: list[re.Pattern] = None):
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


# Define the function to zip a folder, this ignores nested folders
def zip_not_nested_folder(zipf, input_base_path: str, input_folder_path: str, ignore_filenames_regex: list = None):
    # Get the list of files in the specified folder
    filenames = [f for f in os.listdir(input_folder_path)]

    # Zip the files in the folder
    zip_files(zipf, filenames, input_folder_path, input_base_path, ignore_filenames_regex)

    # Log
    input_folder_rel_path = os.path.relpath(input_folder_path, input_base_path)
    print(f'Zipped folder: {input_folder_rel_path}')


# Define the function to zip a folder, this includes nested folders
def zip_nested_folder(zipf, input_base_path: str, input_folder_path: str, ignore_dirs: list[str] = None,
                      ignore_filenames_regex: list[re.Pattern] = None):
    for root, _, filenames in os.walk(input_folder_path):
        # Skip directories in the ignore list
        if ignore_dirs is not None:
            filenames = [f for f in filenames if
                         not any(os.path.relpath(root, input_base_path).startswith(d) for d in ignore_dirs)]

        # Zip the files in the subfolders
        zip_files(zipf, filenames, root, input_base_path, ignore_filenames_regex)

    # Log
    input_folder_rel_path = os.path.relpath(input_folder_path, input_base_path)
    print(f'Zipped folder: {input_folder_rel_path}')