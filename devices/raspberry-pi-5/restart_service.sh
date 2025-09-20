#!/usr/bin/env bash

# Constants
SERVICE_NAME="klevor.service"

# Check if the service exists
if systemctl list-units --all | grep -Fq "$SERVICE_NAME"; then
  echo "Service '$SERVICE_NAME' exists. Restarting now"

  # Restart the service
  sudo systemctl restart "$SERVICE_NAME"
  echo "Service '$SERVICE_NAME' restarted."
else
  echo "Service '$SERVICE_NAME' does not exist or is not loaded. Skipping..."
  exit 0
fi
