import urllib.parse

from .styles import Styles

class SVG:
	"""
	A class to generate SVG strings for WeasyPrint.
	"""

	@staticmethod
	def background_text(
			text: str,
			fill: str,
			font_size: int | str,
			font_family: str = Styles.FONT_FAMILY_SANS_SERIF,
			dominant_baseline: str = "middle",
			text_anchor: str = "middle",
			) -> str:
		"""
		Generates an SVG background text for use in WeasyPrint pages as a background image.

		Args:
			text (str): The text to display in the background.
			fill (str): The fill color for the text.
			font_size (int | str): The font size for the text.
			font_family (str): The font family for the text.
			dominant_baseline (str): The dominant baseline for the text.
			text_anchor (str): The text anchor for the text.
		Returns:
			str: A CSS URL string containing the SVG data.
		"""
		svg = (
			"<svg xmlns='http://www.w3.org/2000/svg' width='100%' viewBox='0 0 100 100'>"
			f"<text x='50%' y='50%' dominant-baseline='{dominant_baseline}' text-anchor='{text_anchor}' "
			f"font-size='{font_size}' font-family='{font_family}' fill='{fill}'>{text}</text></svg>"
		)
		encoded_svg = urllib.parse.quote(svg)
		return f'url("data:image/svg+xml;utf8,{encoded_svg}")'
