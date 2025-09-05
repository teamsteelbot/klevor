#!/usr/bin/env sh
set -e

# Absolute path to this script's directory
SCRIPT_DIR=$(cd "$(dirname "$0")" || exit 1; pwd)

# Path to the source directory and output directory
SOURCE_DIR="${SCRIPT_DIR}/cmd/main"
OUTPUT_DIR="${SCRIPT_DIR}/output/bin/main"

# Check go availability
if ! command -v go >/dev/null 2>&1; then
  echo "Error: go not found in PATH." >&2
  exit 1
fi

# Ensure source directory exists
if [ ! -d "${SOURCE_DIR}" ]; then
  echo "Error: Source directory not found at: ${SOURCE_DIR}" >&2
  exit 1
fi

# Ensure output directory exists
if [ ! -d "${OUTPUT_DIR}" ]; then
  mkdir -p "${OUTPUT_DIR}"
  if [ $? -ne 0 ]; then
    echo "Error: Failed to create output directory at: ${OUTPUT_DIR}" >&2
    exit 1
  fi
fi

echo "Compiling Go the main program..."

go build -o "${OUTPUT_DIR}/main" "${SOURCE_DIR}"

echo "Done."