import os 

# Hailo-related folders
HAILO_DIR = os.path.dirname(os.path.abspath(__file__))
HAILO_LABELS_DIR = os.path.join(HAILO_DIR, 'labels')
HAILO_SUITE_DIR = os.path.join(HAILO_DIR, 'suite')
HAILO_CALIB = 'calib'
HAILO_CALIB_DIR = os.path.join(HAILO_SUITE_DIR, HAILO_CALIB)
HAILO_LIBS_DIR = os.path.join(HAILO_SUITE_DIR, 'libs')
HAILO_MODEL_ZOO_DIR = os.path.join(HAILO_LIBS_DIR, 'model_zoo')
