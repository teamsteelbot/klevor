#!/usr/bin/env bash

# Absolute path to this script's directory
SCRIPT_DIR=$(cd "$(dirname "$0")" || exit 1; pwd)

# Constants
SERVICE_NAME="klevor.service"
SERVICE_PATH="/etc/systemd/system/$SERVICE_NAME"

# Remove the service if it exists
if systemctl list-units --all | grep -Fq "$SERVICE_NAME"; then
  echo "Service '$SERVICE_NAME' exists. Stopping now"

  # Stop the service
  sudo systemctl stop "$SERVICE_NAME"
  echo "Stopped service '$SERVICE_NAME'."

  # Disable the service
  sudo systemctl disable "$SERVICE_NAME"
  echo "Disabled service '$SERVICE_NAME'."

  # Remove the unit file
  sudo rm "$SERVICE_PATH"
  echo "Removed service file at '$SERVICE_PATH'."

  # Reload the daemon
  sudo systemctl daemon-reload
  echo "Reloaded systemd daemon."
  echo "Service '$SERVICE_NAME' has been removed."
else
  echo "Service '$SERVICE_NAME' does not exist or is not loaded. Skipping..."
fi