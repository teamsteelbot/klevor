import os

from .constants import ASSETS_DIR

class SVG:
	"""
	A class to generate SVG strings for WeasyPrint.
	"""

	# SVG for the first page of the PDF
	FIRST_PAGE_SVG = os.path.join(ASSETS_DIR, 'images', 'logo', 'teamsteelbot.png')

	@staticmethod
	def background_text(
			text: str,
			fill: str,
			font_size: int | str,
			dominant_baseline: str = "middle",
			text_anchor: str = "middle",
			) -> str:
		"""
		Generates an SVG background text for use in WeasyPrint pages as a background image.

		Args:
			text (str): The text to display in the background.
			fill (str): The fill color for the text.
			font_size (int | str): The font size for the text.
			dominant_baseline (str): The dominant baseline for the text. Defaults to "middle".
			text_anchor (str): The text anchor for the text. Defaults to "middle".
		Returns:
			str: A CSS URL string containing the SVG data.
		"""
		svg = (
			"<svg xmlns='http://www.w3.org/2000/svg' width='100%' height='100%' viewBox='0 0 100 100'>"
			f"<text x='50%' y='50%' dominant-baseline='{dominant_baseline}' text-anchor='{text_anchor}' "
			f"font-size='{font_size}' fill='{fill}'>{text}</text></svg>"
		)
		return f"url('data:image/svg+xml;utf8,{svg}')"
