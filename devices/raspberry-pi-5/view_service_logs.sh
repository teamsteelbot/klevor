#!/usr/bin/env bash

# Constants
SERVICE_NAME="klevor.service"

# Print the logs
if systemctl list-units --all | grep -Fq "$SERVICE_NAME"; then
  sudo journalctl -u "$SERVICE_NAME"
else
  echo "Service '$SERVICE_NAME' does not exist or is not loaded. Skipping..."
fi