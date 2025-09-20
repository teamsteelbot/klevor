#!/usr/bin/env bash
set -e

# Absolute path to this script's directory
SCRIPT_DIR=$(cd "$(dirname "$0")" || exit 1; pwd)

# Path to script to compile main program
COMPILE_PATH="$SCRIPT_DIR/go/compile_main.sh"

# Path to main binary and Hailo clip script
MAIN_BIN_PATH="$SCRIPT_DIR/go/output/bin/main/main"
RUN_HAILO_CLIP_PATH="$SCRIPT_DIR/run_hailo_clip.sh"

# Ensure script to compile main program exists
if [ ! -f "$COMPILE_PATH" ]; then
    echo "Script to compile main program not found: $COMPILE_PATH"
    exit 1
fi

# Change to the compile script's directory and run it
cd "$(dirname "$COMPILE_PATH")" || exit 1

# Compile main program
"$COMPILE_PATH"

# Change to script's directory
cd "$(dirname "$SCRIPT_DIR")" || exit 1

# Run the main program
echo "Running main program..."

sudo "$MAIN_BIN_PATH" -run-clip-path "$RUN_HAILO_CLIP_PATH"