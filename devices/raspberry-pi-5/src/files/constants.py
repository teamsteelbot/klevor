import os

from ..constants import ROOT_DIR

# Files folder
FILES_DIR = os.path.dirname(os.path.abspath(__file__))

# Hailo-related folders
HAILO_DIR = os.path.join(ROOT_DIR, 'hailo')
HAILO_LABELS_DIR = os.path.join(HAILO_DIR, 'labels')
HAILO_SUITE_DIR = os.path.join(HAILO_DIR, 'suite')
HAILO_CALIB = 'calib'
HAILO_CALIB_DIR = os.path.join(HAILO_SUITE_DIR, HAILO_CALIB)
HAILO_LIBS_DIR = os.path.join(HAILO_SUITE_DIR, 'libs')
HAILO_MODEL_ZOO_DIR = os.path.join(HAILO_LIBS_DIR, 'model_zoo')

# Log-related folders
LOG_DIR = os.path.join(ROOT_DIR, 'log')
LOGS_DIR = os.path.abspath(os.path.join(ROOT_DIR, '..', 'logs'))

# YOLO folder
YOLO_DIR = os.path.abspath(os.path.dirname(__file__))

# YOLO runs
RUNS_OLD = 'runs_old'
RUNS = 'runs'

# YOLO weights
WEIGHTS = 'weights'

# Directories to ignore always
IGNORE_DIRS = (
    '.git', '__pycache__', '.idea', '.vscode', '.venv', 'venv', 'env')
