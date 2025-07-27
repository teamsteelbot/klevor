import os

from bs4 import BeautifulSoup, Tag
from weasyprint import HTML, CSS

from .constants import (
	PDF_DIR,
	DOWNLOADS_DIR,
    DOCS_DIR
	)
from .utils import join_styles
from .styles import Styles
from .measure import Measure

class PDF:
	"""
	A class to handle PDF generation for WeasyPrint
	"""

	# PDF output file
	PDF_OUTPUT_FILE = os.path.join(DOWNLOADS_DIR, 'teamsteelbot.pdf')

	# PDF DPI
	PDF_DPI = 300

	# PDF base URL
	PDF_BASE_URL = DOCS_DIR

	# Team logo SVG path
	TEAM_SVG = "assets/images/logo/teamsteelbot.png"

	# Team logo image height
	TEAM_LOGO_HEIGHT = Measure(30, Measure.MM_UNIT)

	def __init__(self, styles_inst: Styles):
		"""
		Initializes the PDF class with the given styles.

		Args:
			styles_inst (Styles): An instance of the Styles class containing CSS styles.
		"""
		# Store the styles instance
		self.__styles = styles_inst

		# Initialize any necessary attributes or configurations here
		self.__soup = BeautifulSoup('', 'html.parser')
		self.__html_tag = self.__soup.new_tag('html')
		self.__html_body_tag = self.__soup.new_tag('body')
		self.__styles_files = []
		self.__runtime_styles = []

		# Append BeautifulSoup tags
		self.__soup.append(self.__html_tag)
		self.__html_tag.append(self.__html_body_tag)

	def div_with_page_selector(
			self,
			page_selector: str,
			content: str = ''
		) -> Tag:
		"""
		Generates a div with a specific page selector for WeasyPrint.

		Args:
			page_selector (str): The CSS selector for the page.
			content (str): Optional content to include within the div.
		Returns:
			Tag: A BeautifulSoup Tag object representing the div with the page selector.
		"""
		div_tag = self.__soup.new_tag('div', style=f'page: {page_selector};')
		if content:
			div_tag.string = content
		return div_tag

	def break_page(self) -> Tag:
		"""
		Generates a page break for WeasyPrint.

		Returns:
			Tag: A BeautifulSoup Tag object representing a page break.
		"""
		return self.__soup.new_tag('div', **{'class': 'page-break'})

	def team_logo(
			self,
			height: Measure = TEAM_LOGO_HEIGHT,
		) -> Tag:
		"""
		Generates the HTML for the team logo.

		Args:
			height (Measure): The height of the team logo image.
		Returns:
			Tag: A BeautifulSoup Tag object representing the team logo image.
		"""

		# Create the styles map
		runtime_styles = {}
		if height:
			runtime_styles['height'] = str(height)

		return self.__soup.new_tag(
			'img',
			src=self.TEAM_SVG,
			style=join_styles(runtime_styles),
			alt='Team SteelBot Logo'
			)

	def center_tag(
			self,
			tag: Tag,
			) -> Tag:
		"""
		Centers a BeautifulSoup Tag within a div.

		Args:
			tag (Tag): The BeautifulSoup Tag to center.
		Returns:
			Tag: A BeautifulSoup Tag object representing the centered div.
		"""
		# Check if the tag has a height
		tag_style = tag.get('style')
		if tag_style is None:
			raise ValueError("Tag does not have a style attribute with height defined.")

		tag_height = tag_style.get('height')
		if tag_height is None:
			raise ValueError("Tag does not have a height defined in its style.")

		# Parse as a Measure object
		tag_height = Measure.parse_style_measure(tag_height)

		# Calculate the margin top to center the tag
		margin_top = (
			self.__styles.page_height.value - self.__styles.page_margin - tag_height
		) / 2

		# Create a div with the horizontally centered class
		hcenter_div = self.__soup.new_tag('div', **{
			'class': self.__styles.HCENTER_CLASS,
			})

	def add_tag(self, tag: Tag, runtime_styles: str = '', break_page: bool = True):
		"""
		Adds a BeautifulSoup Tag to the PDF document.

		Args:
			tag (Tag): The BeautifulSoup Tag to add to the PDF document.
			runtime_styles (str): Custom CSS styles to apply
			break_page (bool): Whether to insert a page break after the content.
		"""
		self.__html_body_tag.append(tag)
		if runtime_styles:
			self.__runtime_styles.append(runtime_styles)
		if break_page:
			self.__html_body_tag.append(self.break_page())

	def save(
			self,
			base_url: str = PDF_BASE_URL,
			output_file: str = PDF_OUTPUT_FILE,
			optimize_images: bool = True,
			dpi: int = PDF_DPI
		):
		"""
		Saves the PDF document to the specified output file.

		Args:
			base_url (str): The base URL for the HTML content.
			output_file (str): The path to the output PDF file.
			optimize_images (bool): Whether to optimize images in the PDF.
			dpi (int): The DPI for the PDF output.
		"""

		# Check if the output file is a valid path
		if not os.path.exists(os.path.dirname(output_file)):
			os.makedirs(os.path.dirname(output_file))

		# Generate the PDF from the HTML content
		print(f'Saving PDF to {output_file}...')
		HTML(
			string=str(self.__html_tag),
			base_url=base_url
		).write_pdf(
			output_file,
			stylesheets=[
				CSS(self.__styles.stylesheet_file),
				CSS(string='\n'.join(self.__runtime_styles)),
			],
			optimize_images=optimize_images,
			dpi=dpi,
			)
		print(f'PDF saved to {output_file}')