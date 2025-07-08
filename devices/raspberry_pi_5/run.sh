#!/bin/bash

# Activate the virtual environment
source .venv/bin/activate

# Run the main application
python -m src --debug --version v11 --rplidar-is-upside-down \
  --rplidar-angle-rotation -90.0