import os
import re

from qrcode import QRCode
from qrcode.image.svg import SvgPathImage

from .constants import (
	ERROR_CORRECTION,
	BOX_SIZE,
	BORDER,
	PAGE_URL,
	FILL_COLOR_DARK,
	QR_DARK_PATH,
	FILL_COLOR_LIGHT,
	QR_LIGHT_PATH,
	)

# Create QR code object with the highest error correction
qr = QRCode(
    version=None,  # Automatic sizing
    error_correction=ERROR_CORRECTION,
    box_size=BOX_SIZE,
    border=BORDER,
	image_factory=SvgPathImage
)
qr.add_data(PAGE_URL)
qr.make(fit=True)

for fill, path in [
	(FILL_COLOR_DARK, QR_DARK_PATH),
	(FILL_COLOR_LIGHT, QR_LIGHT_PATH)
]:
	# Create image with transparency
	img = qr.make_image()
	img_str = img.to_string(encoding='unicode')

	# Replace fill color in the SVG string as a Regex pattern
	img_str = re.sub(r'fill="#[0-9a-fA-F]{6}"', f'fill="{fill}"', img_str)

	# Check if the directory exists, create it if not
	if not os.path.exists(os.path.dirname(path)):
		os.makedirs(os.path.dirname(path))

	# Save the SVG file
	with open(path, 'w', encoding='utf-8') as f:
		f.write(img_str)