import os
from uuid import uuid4
from typing import Callable

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
	TEAM_LOGO_HEIGHT = Measure(60, Measure.MM_UNIT)

	@staticmethod
	def normalize_images_src(soup, normpath_fn: Callable[[str], str]):
		"""
		Normalizes the src attributes of <img> tags in the BeautifulSoup object.

		Args:
			soup (BeautifulSoup): The BeautifulSoup object containing HTML content.
			normpath_fn (Callable[[str], str]): A function to normalize the image paths.
		"""
		# Iterate over all <img> tags to convert relative paths
		images = soup.find_all('img')
		for img in images:
			img_src = img.get('src')
			if img_src and not img_src.startswith(('http://', 'https://')):
				# Convert relative image paths
				img_src = normpath_fn(img_src)
				img['src'] = img_src

	def __init__(self, styles_inst: Styles, base_url: str = PDF_BASE_URL):
		"""
		Initializes the PDF class with the given styles.

		Args:
			styles_inst (Styles): An instance of the Styles class containing CSS styles.
			base_url (str): The base URL for the HTML content.
		"""
		# Store the styles instance and base URL
		self.__styles = styles_inst
		self.__base_url = base_url

		# Initialize any necessary attributes or configurations here
		self.__soup = BeautifulSoup('', 'html.parser')
		self.__html_tag = self.__soup.new_tag('html')
		self.__html_body_tag = self.__soup.new_tag('body')
		self.__styles_files = []
		self.__runtime_styles = []
		self.__section_counter = 0

		# Append BeautifulSoup tags
		self.__soup.append(self.__html_tag)
		self.__html_tag.append(self.__html_body_tag)

		# Initialize a map for runtime ID
		self.__runtime_ids = {}

	def normalize_headers_id(self, soup: BeautifulSoup, relative_file_path: str):
		"""
		Normalizes the ID attributes of header tags in the BeautifulSoup object.

		Args:
			soup (BeautifulSoup): The BeautifulSoup object containing HTML content.
			relative_file_path (str): The path to the Markdown file being processed relative to the base URL.
		"""
		# Iterate over all <h1> to <h6> tags to remove the ID from the header text
		headers = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
		for header in headers:
			header_text = header.get_text()
			for prefix in ['{:#', '{#']:
				if prefix not in header_text:
					continue

				# Remove the ID from the header text
				header_split = header_text.split(prefix)
				header_text = header_split[0]
				header_id = header_split[1]
				header.string = header_text.strip()

				# Normalize the header ID and check if it's on the runtime IDs map
				header_id = header_id.strip('}').strip()
				header_relative_path_id = f'{relative_file_path}#{header_id}'
				if header_relative_path_id not in self.__runtime_ids:
					# If the ID is not in the map, generate a new ID
					new_id = uuid4()
					self.__runtime_ids[header_relative_path_id] = new_id

				# Set the ID attribute of the header tag
				header.id = self.__runtime_ids[header_relative_path_id]

	def div_with_page_selector(
			self,
			page_selector: str,
			tag: Tag
		) -> Tag:
		"""
		Generates a div with a specific page selector for WeasyPrint.

		Args:
			page_selector (str): The CSS selector for the page.
			tag (Tag): The BeautifulSoup Tag to include in the div.
		Returns:
			Tag: A BeautifulSoup Tag object representing the div with the page selector.
		"""
		div_tag = self.__soup.new_tag('div', style=f'page: {page_selector};')
		div_tag.append(tag)
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

	def section_title(self, text: str) -> Tag:
		"""
		Generates a title tag for a section in the PDF document.

		Args:
			text (str): The title text for the section.
		Returns:
			Tag: A BeautifulSoup Tag object representing the title.
		"""
		h1_tag = self.__soup.new_tag(
			'h1',
			style=join_styles({
				'font-family': self.__styles.font_family_monospace,
				'font-size': self.__styles.font_size_h1_section,
				'height': self.__styles.font_size_h1_section,
				'line-height': 1,
				'color': self.__styles.font_color_h1_section,
				'justify-content': 'center',
				'text-transform': 'uppercase',
				})
			)
		h1_tag.string = text
		return h1_tag

	def center_tag(
			self,
			tag: Tag,
			center_vertically: bool = True,
			center_horizontally: bool = True,
		) -> Tag:
		"""
		Centers a BeautifulSoup Tag within a div.

		Args:
			tag (Tag): The BeautifulSoup Tag to center.
			center_vertically (bool): Whether to center the tag vertically.
			center_horizontally (bool): Whether to center the tag horizontally.
		Returns:
			Tag: A BeautifulSoup Tag object representing the centered div.
		"""
		# Initialize center styles map
		center_styles = {}

		if center_vertically:
			# Extract the style attribute from the tag
			tag_style = tag.get('style')
			if tag_style is None:
				raise ValueError("Tag does not have a style attribute with height defined.")

			# Extract the height from the tag's style
			tag_style = Styles.parse_style_as_dict(tag_style)
			tag_height = tag_style.get('height')
			if tag_height is None:
				raise ValueError("Tag does not have a height defined in its style.")

			# Parse as a Measure object
			tag_height = Measure.parse_style_measure(tag_height)

			# Calculate the margin top to center the tag
			margin_top = (
				self.__styles.page_height / 2 - self.__styles.page_margin - tag_height / 2
			) / 2

			# Add the margin top to the center styles
			center_styles['style'] = f'margin-top: {str(margin_top)}'

		if center_horizontally:
			# Add horizontal centering class
			center_styles['class'] = self.__styles.HCENTER_CLASS

		# Create a div with the horizontally centered class
		hcenter_div = self.__soup.new_tag('div', **center_styles)
		hcenter_div.append(tag)
		return hcenter_div

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

	def add_first_page(
			self,
			tag: Tag
		):
		"""
		Adds the first page of the PDF document with a custom HTML content.

		Args:
			tag (Tag): The BeautifulSoup Tag to add to the first page.
		"""
		center_tag = self.center_tag(tag)
		first_page_tag = self.div_with_page_selector(
			self.__styles.FIRST_PAGE_SELECTOR,
			center_tag
		)
		custom_styles = self.__styles.first_page()
		self.add_tag(first_page_tag, custom_styles, False)

	def add_section_page(
			self,
			tag: Tag,
			top_right_content: str = '',
		):
		"""
		Adds a section page to the PDF document with a custom HTML content.

		Args:
			tag (Tag): The BeautifulSoup Tag to add to the section page.
			top_right_content (str): Custom CSS styles to apply.
		"""
		self.__section_counter += 1
		page_selector = f'section-{self.__section_counter}'
		center_tag = self.center_tag(tag)
		section_tag = self.div_with_page_selector(page_selector, center_tag)
		custom_styles = self.__styles.section_page(
			page_selector=page_selector,
			top_right_content=top_right_content,
			)
		self.add_tag(section_tag, custom_styles, False)

	def add_section_body(
			self,
			tag: Tag,
			top_right_content: str = '',
		):
		"""
		Adds a section body to the PDF document with a custom HTML content.

		Args:
			tag (Tag): The BeautifulSoup Tag to add to the section body.
			top_right_content (str): Custom CSS styles to apply.
		"""
		page_selector = f'section-{self.__section_counter}-body'
		section_body_tag = self.div_with_page_selector(page_selector, tag)
		custom_styles = self.__styles.section_body(
			page_selector=page_selector,
			top_right_content=top_right_content,
			)
		self.add_tag(section_body_tag, custom_styles, False)


	def save(
			self,
			output_file: str = PDF_OUTPUT_FILE,
			optimize_images: bool = True,
			dpi: int = PDF_DPI
		):
		"""
		Saves the PDF document to the specified output file.

		Args:
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
			base_url=self.__base_url
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