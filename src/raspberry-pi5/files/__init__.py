import os
import shutil

# Directories to ignore always
IGNORE_DIRS = ['.git', '__pycache__', '.idea', '.vscode', '.venv', 'venv', 'env']

# Move file between folders
def move_file(input_path, output_dir):
    if os.path.exists(input_path):
        shutil.move(input_path, output_dir)


# Move folder between folders
def move_folder(input_dir, output_dir):
    if os.path.exists(input_dir):
        shutil.move(input_dir, output_dir)


# Move folder content to another folder
def move_folder_content(input_dir, output_dir):
    if os.path.exists(input_dir):
        # Get all files and folders in the input directory
        for item in os.listdir(input_dir):
            item_path = os.path.join(input_dir, item)

            # Move each item to the output directory
            shutil.move(item_path, output_dir)

# Copy file between folders
def copy_file(input_path, output_path):
    if os.path.exists(input_path):
        shutil.copy(input_path, output_path)
