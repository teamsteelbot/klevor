#!/bin/bash

echo "Activating virtual environment..."
source ./.venv/bin/activate

echo "Generating PDF..."
python -m pdf

echo "PDF generation complete."