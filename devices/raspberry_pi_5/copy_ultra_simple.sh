set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

SRC="$SCRIPT_DIR/rplidar-sdk/output/Linux/Release/ultra_simple"
DST1="$SCRIPT_DIR/go/output/bin/tests/bin"
DST2="$SCRIPT_DIR/go/output/bin/main/bin"

echo "Copy Slamtec ultra_simple program from rplidar-sdk folder to output binary folders..."

if [ ! -f "$SRC" ]; then
    echo "Source file not found: $SRC"
    exit 0
fi

for dst in "$DST1" "$DST2"; do
    if [ ! -d "$dst" ]; then
        echo "Destination directory not found: $dst, creating it."
        mkdir -p "$dst"
    fi
done

cp "$SRC" "$DST1"
cp "$SRC" "$DST2"
echo "Done."