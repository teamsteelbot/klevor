#!/bin/bash

echo "Activating virtual environment..."
source ./.venv/bin/activate

echo "Generating QR codes..."
python -m qr

echo "QR codes generation complete."