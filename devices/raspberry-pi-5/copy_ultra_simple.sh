#!/usr/bin/env sh
set -e

# Absolute path to this script's directory
SCRIPT_DIR=$(cd "$(dirname "$0")" || exit 1; pwd)

# RPLiDAR SDK submodule directory
RPLIDAR_SDK_DIR="$SCRIPT_DIR/rplidar-sdk"

# Source and destination paths
SOURCE_FILE="$RPLIDAR_SDK_DIR/output/Linux/Release/ultra_simple"
DESTINATION_DIR1="$SCRIPT_DIR/go/output/bin/tests/bin"
DESTINATION_DIR2="$SCRIPT_DIR/go/output/bin/main/bin"

echo "Copy Slamtec ultra_simple program from rplidar-sdk folder to output binary folders..."

# Ensure RPLIDAR SDK directory exists
if [ ! -d "$RPLIDAR_SDK_DIR" ]; then
    echo "RPLIDAR SDK directory not found: $RPLIDAR_SDK_DIR"
    exit 0
fi

# Ensure source file exists
if [ ! -f "$SOURCE_FILE" ]; then
    echo "Source file not found: $SOURCE_FILE"
    exit 0
fi

# Ensure destination directories exist
for dst in "$DESTINATION_DIR1" "$DESTINATION_DIR2"; do
    if [ ! -d "$dst" ]; then
        echo "Destination directory not found: $dst, creating it."
        mkdir -p "$dst"
    fi
done

cp "$SOURCE_FILE" "$DESTINATION_DIR1"
cp "$SOURCE_FILE" "$DESTINATION_DIR2"
echo "Done."