#!/bin/bash

echo "Activating virtual environment..."
source ./.venv/bin/activate

echo "Update the PDF..."
python -m pdf

echo "Deploying MkDocs site to remote..."
mkdocs gh-deploy --remote-name dev

echo "Deployment complete."