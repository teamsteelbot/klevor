#!/usr/bin/env sh
set -e

# Absolute path to this script's directory
SCRIPT_DIR=$(cd "$(dirname "$0")" || exit 1; pwd)

# Path to the main.go and output file 
MAIN_GO="${SCRIPT_DIR}/cmd/main/main.go"
OUTPUT_DIR="${SCRIPT_DIR}/output/bin/main"
OUTPUT_FILE="${OUTPUT_DIR}/flash.uf2"

# Check tinygo availability
if ! command -v tinygo >/dev/null 2>&1; then
  echo "Error: tinygo not found in PATH." >&2
  exit 1
fi

# Ensure source file exists
if [ ! -f "${MAIN_GO}" ]; then
  echo "Error: Main file not found at: ${MAIN_GO}" >&2
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

echo "Compiling TinyGo program..."

tinygo build -o="${OUTPUT_FILE}" -target=pico2-w -size=full -print-allocs=. "${MAIN_GO}"

echo "Done."