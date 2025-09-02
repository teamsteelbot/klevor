#!/usr/bin/env sh
set -e

# Absolute path to this script's directory
SCRIPT_DIR=$(cd "$(dirname "$0")" || exit 1; pwd)

# Hailo CLIP submodule directory
HAILO_CLIP_DIR="$SCRIPT_DIR/hailo-clip"

# Setup env script path
SETUP_ENV_SCRIPT="$HAILO_CLIP_DIR/setup_env.sh"

# Text image matcher script path
TEXT_IMAGE_MATCHER_PATH="$HAILO_CLIP_DIR/clip_app/text_image_matcher.py"

# Embeddings path
EMBEDDINGS_PATH="$HAILO_CLIP_DIR/embeddings.json"

# Script arguments
JSON_PATH=""

usage() {
    echo "Usage: $(basename "$0") --json-path <input.json>"
    echo "  --json-path    Path to input JSON (required)"
    echo "  -h|--help      Show help"
    exit 1
}

# Parse args (only long option json-path)
while [ $# -gt 0 ]; do
    case "$1" in
        --json-path)
            [ -n "${2:-}" ] || usage
            JSON_PATH=$2
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        --)
            shift
            break
            ;;
        *)
            echo "Unknown argument: $1" >&2
            usage
            ;;
    esac
done

# Ensure required arguments are provided
if [ ! -n "$JSON_PATH" ]; then
    echo "Missing --json-path" >&2
    usage
fi

# Ensure input JSON exists
if [ ! -f "$JSON_PATH" ]; then
    echo "Input JSON not found: $JSON_PATH" >&2
    exit 1
fi

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

# Ensure setup env script exists
if [ ! -f "$SETUP_ENV_SCRIPT" ]; then
    echo "Setup environment script not found: $SETUP_ENV_SCRIPT"
    exit 1
fi

# Ensure text image matcher script exists
if [ ! -f "$TEXT_IMAGE_MATCHER_PATH" ]; then
    echo "Text image matcher script not found: $TEXT_IMAGE_MATCHER_PATH"
    exit 1
fi

echo "Setting up the virtual environment..."

# Source the setup_env.sh script to set up the virtual environment
. "$SETUP_ENV_SCRIPT"

echo "Generating CLIP embeddings..."

# Run the text_image_matcher.py script to generate embeddings
python3 "$TEXT_IMAGE_MATCHER_PATH" --texts-json "$JSON_PATH" --output_json "$EMBEDDINGS_PATH"

echo "Done."