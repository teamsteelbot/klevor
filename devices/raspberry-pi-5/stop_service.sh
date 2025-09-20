#!/user/bin/env bash

# Constants
SERVICE_NAME="klevor.service"

# Remove the service if it exists
if systemctl list-units --all | grep -Fq "$SERVICE_NAME"; then
  echo "Service '$SERVICE_NAME' exists. Stopping now"

  # Stop the service
  sudo systemctl stop "$SERVICE_NAME"
else
  echo "Service '$SERVICE_NAME' does not exist or is not loaded. Skipping..."
fi