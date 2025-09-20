#!/usr/bin/env bash

# Absolute path to this script's directory
SCRIPT_DIR=$(cd "$(dirname "$0")" || exit 1; pwd)

# Constants
SERVICE_NAME="klevor.service"
SERVICE_PATH="/etc/systemd/system/$SERVICE_NAME"
REMOVE_SERVICE_PATH="$SCRIPT_DIR/remove_service.sh"
EXEC_PATH="$SCRIPT_DIR/run_service.sh"

# Remove existing service if it exists
sudo bash "$REMOVE_SERVICE_PATH"

# Create the unit file
cat > "$SERVICE_PATH" << EOF
[Unit]
Description=Klevor Startup Service
After=multi-user.target

[Service]
User=pi
ExecStart=$EXEC_PATH
StandardOutput=inherit
StandardError=inherit
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

# Reload daemon
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable $SERVICE_NAME
