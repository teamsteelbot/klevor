#!/usr/bin/env bash

# Absolute path to this script's directory
SCRIPT_DIR=$(cd "$(dirname "$0")" || exit 1; pwd)

# Constants
USER="ralva"
SERVICE_NAME="klevor.service"
SERVICE_PATH="/etc/systemd/system/$SERVICE_NAME"
REMOVE_SERVICE_PATH="$SCRIPT_DIR/remove_service.sh"
EXEC_PATH="$SCRIPT_DIR/run_service.sh"
TIMEOUT=15

# Remove existing service if it exists
sudo "$REMOVE_SERVICE_PATH"

# Create the unit file
sudo cat > "$SERVICE_PATH" << EOF
[Unit]
Description=Klevor Startup Service
After=multi-user.target

[Service]
User=$USER
ExecStart=$EXEC_PATH
Environment="PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/local/go/bin:/usr/bin/git"
Environment="DISPLAY=:0"
Environment="XAUTHORITY=/home/ralva/.Xauthority"
TimeoutStopSec=${TIMEOUT}s
WorkingDirectory=$SCRIPT_DIR
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

echo "Created service file at '$SERVICE_PATH'."
echo "Set to run as user '$USER' with working directory '$SCRIPT_DIR'."

# Reload daemon
sudo systemctl daemon-reload
echo "Reloaded systemd daemon."

# Enable service
sudo systemctl enable $SERVICE_NAME
echo "Enabled service '$SERVICE_NAME'."
