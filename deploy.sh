#!/bin/bash

echo "Activating virtual environment..."
source ./.venv/bin/activate

echo "Deploying MkDocs site to remote..."
mkdocs gh-deploy --remote-name dev

echo "Deployment complete."