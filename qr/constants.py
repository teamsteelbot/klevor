import os

from qrcode.constants import ERROR_CORRECT_H

# Data to encode
PAGE_URL = "https://klevor.ralvarez.dev"

# QR Code configuration constants
ERROR_CORRECTION = ERROR_CORRECT_H
BOX_SIZE = 10
BORDER = 4

# Fill colors
FILL_COLOR_LIGHT = "#212529"
FILL_COLOR_DARK = "#f8f9fa"

# Root directory of the project
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Assets directories
ASSETS_DIR = os.path.join(ROOT_DIR, 'assets')
IMAGES_DIR = os.path.join(ASSETS_DIR, 'images')
QR_DIR = os.path.join(IMAGES_DIR, 'qr')

# Directory for saving QR codes
QR_LIGHT_PATH = os.path.join(QR_DIR, 'page-url--light.svg')
QR_DARK_PATH = os.path.join(QR_DIR, 'page-url--dark.svg')