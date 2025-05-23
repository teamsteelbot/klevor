import os
import shutil

# Environments
ENVIRONMENT_LOCAL = "local"
ENVIRONMENT_COLAB = "colab"

# Google Drive API calls limit
GOOGLE_DRIVE_API_LIMIT_PERIOD = 100
GOOGLE_DRIVE_API_LIMIT_CALLS = 20000
GOOGLE_DRIVE_API_CALL_DELAY = GOOGLE_DRIVE_API_LIMIT_PERIOD / GOOGLE_DRIVE_API_LIMIT_CALLS * 2

# Batch size
BATCH_SIZE = 1000

# Directories to ignore always
IGNORE_DIRS = ['.git', '__pycache__', '.idea', '.vscode', '.venv', 'venv', 'env']

def move_file(input_path, output_dir):
    """
    Move file between folders.
    """
    if os.path.exists(input_path):
        shutil.move(input_path, output_dir)


def move_folder(input_dir, output_dir):
    """
    Move folder between folders.
    """
    if os.path.exists(input_dir):
        shutil.move(input_dir, output_dir)


def move_folder_content(input_dir, output_dir):
    """
    Move folder content to another folder.
    """
    if os.path.exists(input_dir):
        # Check if the output directory exists, if not create it
        ensure_path_exists(output_dir)

        # Get all files and folders in the input directory
        for item in os.listdir(input_dir):
            item_input_path = os.path.join(input_dir, item)
            item_output_path = os.path.join(output_dir, item)

            # Check if it's a file or folder
            if os.path.isdir(item_input_path):
                pass

            # Check if the item already exists in the output directory
            elif not os.path.exists(item_output_path):
                pass

            # Delete the item if it already exists in the output directory
            else:
                os.remove(item_output_path)


            # Move each item to the output directory
            shutil.move(item_input_path, output_dir)

def copy_file(input_path, output_path):
    """
    Copy a file from input_path to output_path.
    """
    if os.path.exists(input_path):
        shutil.copy(input_path, output_path)

def ensure_path_exists(output_path):
    """
    Ensure the path exists, if not create it.
    """
    # Check if it contains an extension
    if os.path.splitext(output_path)[1]:
        output_dir = os.path.dirname(output_path)
    else:
        output_dir = output_path

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
