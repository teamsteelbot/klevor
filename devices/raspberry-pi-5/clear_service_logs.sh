#!/usr/bin/env bash

# Constants
SERVICE_NAME="klevor.service"

# Check if the service exists
if systemctl list-units --all | grep -Fq "$SERVICE_NAME"; then
  echo "Service '$SERVICE_NAME' exists. Clearing logs now"

  # Clear the logs
  sudo journalctl --rotate
  sudo journalctl --unit=$SERVICE_NAME --vacuum-time=1s
else
  echo "Service '$SERVICE_NAME' does not exist or is not loaded. Skipping..."
  exit 0
fi