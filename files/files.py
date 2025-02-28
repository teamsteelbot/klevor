import os
import shutil


# Move file between folders
def move_file(input_path, output_dir):
    if os.path.exists(input_path):
        shutil.move(input_path, output_dir)


# Move folder between folders
def move_folder(input_dir, output_dir):
    if os.path.exists(input_dir):
        shutil.move(input_dir, output_dir)


# Copy file between folders
def copy_file(input_path, output_path):
    if os.path.exists(input_path):
        shutil.copy(input_path, output_path)
