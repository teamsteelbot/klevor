#!/usr/bin/env sh
set -e

# Absolute path to this script's directory
SCRIPT_DIR=$(cd "$(dirname "$0")" || exit 1; pwd)

# Path to the test main.go
MAIN_GO="${SCRIPT_DIR}/cmd/tests/escmotor/main.go"

# Check tinygo availability
if ! command -v tinygo >/dev/null 2>&1; then
  echo "Error: tinygo not found in PATH." >&2
  exit 1
fi

# Ensure source file exists
if [ ! -f "${MAIN_GO}" ]; then
  echo "Error: Test file not found at: ${MAIN_GO}" >&2
  exit 1
fi

echo "Compiling and flashing TinyGo ESC Motor test to Raspberry Pi Pico 2W..."

tinygo flash -target pico2-w "${MAIN_GO}"

echo "Done."