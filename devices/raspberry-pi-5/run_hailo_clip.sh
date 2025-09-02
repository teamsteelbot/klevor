#!/usr/bin/env sh
set -e

# Absolute path to this script's directory
SCRIPT_DIR=$(cd "$(dirname "$0")" || exit 1; pwd)

# Hailo CLIP submodule directory
HAILO_CLIP_DIR="$SCRIPT_DIR/hailo-clip"

# Setup env script path
SETUP_ENV_SCRIPT="$HAILO_CLIP_DIR/setup_env.sh"

# Hailo CLIP application path
HAILO_CLIP_APP_PATH="$HAILO_CLIP_DIR/clip_application.py"

# Check for python3 availability
if ! command -v python3 >/dev/null 2>&1; then
    echo "Error: python3 not found in PATH." >&2
    exit 1
fi

# Ensure Hailo CLIP directory exists
if [ ! -d "$HAILO_CLIP_DIR" ]; then
    echo "Hailo CLIP directory not found: $HAILO_CLIP_DIR"
    exit 1
fi

# Ensure Hailo CLIP application exists
if [ ! -f "$HAILO_CLIP_APP_PATH" ]; then
    echo "Hailo CLIP application not found: $HAILO_CLIP_APP_PATH"
    exit 1
fi

echo "Setting up the virtual environment..."

# Source the setup_env.sh script to set up the virtual environment
. "$SETUP_ENV_SCRIPT"

echo "Calling the Hailo CLIP application..."

# Run the Hailo CLIP application
python3 "$HAILO_CLIP_APP_PATH" --i rpi --disable-runtime-prompts

echo "Done."