import os

from .utils import join_styles
from .constants import PDF_DIR
from .measure import Measure

class Styles:
	"""
	Styles class for generating CSS styles for WeasyPrint and that also
	provides the constant styles used in the PDF generation.
	"""

	# Custom styles
	ROOT_CLASS = ':root'
	FONT_SIZE_H1_SECTION = '--font-size--h1--section'
	FONT_COLOR_H1_SECTION = '--font-color--h1--section'
	FONT_FAMILY_SANS_SERIF = '--font-family--sans-serif'
	FONT_FAMILY_MONOSPACE = '--font-family--monospace'
	PAGE_BACKGROUND_COLOR_FIRST_PAGE = '--page-background-color--first-page'
	PAGE_BACKGROUND_COLOR_SECTION_PAGE = '--page-background-color--section-page'
	PAGE_FORMAT = '--page-format'
	PAGE_MARGIN = '--page-margin'

	# Page format values
	PAGE_FORMAT_A4 = 'A4'

	# Page format sizes
	PAGE_FORMAT_A4_HEIGHT = Measure(297, Measure.MM_UNIT)

	# First page selector
	FIRST_PAGE_SELECTOR = 'first'

	# Horizontally centering class
	HCENTER_CLASS = 'hcenter'

	# WeasyPrint stylesheet files
	STYLESHEET_FILE = os.path.join(PDF_DIR, 'styles.css')

	@staticmethod
	def parse_style_as_dict(style: str) -> dict:
		"""
		Parses a style string and returns a dictionary of styles.

		Args:
			style (str): The style string to parse.

		Returns:
			dict: A dictionary containing the parsed styles.
		"""
		if not style:
			return {}
		raw_styles = style.split(';')
		raw_styles = [s.strip() for s in raw_styles if s.strip()]
		return {k.strip(): v.strip() for k, v in (s.split(':', 1) for s in raw_styles if ':' in s)}

	def __init__(self, stylesheet_file: str = STYLESHEET_FILE):
		"""
		Initializes the Styles class.

		Args:
			stylesheet_file (str): The path to the stylesheet file.
		"""
		# Parse the stylesheet file
		with open(stylesheet_file, 'r', encoding='utf-8') as file:
			# Store the stylesheet file
			self.__stylesheet_file = stylesheet_file

			# Read the content of the stylesheet file
			self.__stylesheet_content = file.read()

			# Read the classes from the stylesheet
			raw_classes = self.__stylesheet_content.split('}')
			raw_classes = [c.strip() for c in raw_classes if c.strip()]
			self.__classes = {}
			for cls in raw_classes:
				if not cls:
					continue

				# Split the class name and its styles
				name, styles = cls.split('{', 1)
				name = name.strip()

				# Store the class name and its styles
				self.__classes[name] = self.parse_style_as_dict(styles)

		# Check if the required selectors are present
		for selector in [
			self.ROOT_CLASS,
			*['.' + cls for cls in [
				self.HCENTER_CLASS
			]
			]]:
			if selector not in self.__classes:
				raise RuntimeError(
					f"Selector '{selector}' not found in the stylesheet.",
					)

		# Store the root class styles
		self.__root_class_styles = self.__classes.get(self.ROOT_CLASS)

		# Check if the required styles are present in the root class styles
		for style in [
			self.FONT_SIZE_H1_SECTION,
			self.FONT_COLOR_H1_SECTION,
			self.FONT_FAMILY_SANS_SERIF,
			self.FONT_FAMILY_MONOSPACE,
			self.PAGE_BACKGROUND_COLOR_FIRST_PAGE,
			self.PAGE_BACKGROUND_COLOR_SECTION_PAGE,
			self.PAGE_FORMAT,
			self.PAGE_MARGIN,
			]:
			if style not in self.__root_class_styles:
				raise RuntimeError(
					f"Style '{style}' not found in the root class styles.",
					)

		# Initialize the styles
		self.__font_size_h1_section = self.__root_class_styles.get(
			self.FONT_SIZE_H1_SECTION
			)
		self.__font_color_h1_section = self.__root_class_styles.get(
			self.FONT_COLOR_H1_SECTION
			)
		self.__font_family_sans_serif = self.__root_class_styles.get(
			self.FONT_FAMILY_SANS_SERIF,
			)
		self.__font_family_monospace = self.__root_class_styles.get(
			self.FONT_FAMILY_MONOSPACE,
			)
		self.__page_format = self.__root_class_styles.get(
			self.PAGE_FORMAT,
			)
		self.__page_background_color_first_page = self.__root_class_styles.get(
			self.PAGE_BACKGROUND_COLOR_FIRST_PAGE,
			)
		self.__page_background_color_section_page = self.__root_class_styles.get(
			self.PAGE_BACKGROUND_COLOR_SECTION_PAGE,
			)
		self.__page_margin = self.__root_class_styles.get(
			self.PAGE_MARGIN,
			)

		# Get the page height based on the page format
		if self.__page_format == self.PAGE_FORMAT_A4:
			self.__page_height = self.PAGE_FORMAT_A4_HEIGHT
		else:
			raise ValueError("Page format height is not defined.")

		# Get the page margin as a Measure object
		self.__page_margin = Measure.parse_style_measure(
			self.__page_margin,
		)

	@staticmethod
	def page(
			page_selector: str,
			background_color: str = 'transparent',
			background_image: str = 'none',
			background_repeat: str = 'no-repeat',
			background_position: str = 'center center',
			background_size: str = 'auto',
			top_right_content: str = '',
			bottom_center_content: str = '',
			) -> str:
		"""
	    Generates CSS for a specific page of a PDF document with a specified background.
	
	    Args:
	    	page_selector (str): The CSS selector for the page.
			background_color (str): The background color for the page.
			background_image (str): The background image for the page, formatted as a CSS URL.
	        background_repeat (str): The repeat style for the background image.
	        background_position (str): The position of the background image.
	        background_size (str): The size of the background image.
			top_right_content (str): Content for the top-right corner of the page.
			bottom_center_content (str): Content for the bottom-center of the page.
	    Returns:
	        str: The complete CSS string for the specified page.
	        :param background_image:
	    """

		# Attributes for the page background
		attr = {}
		if background_color:
			attr['background-color'] = background_color
		if background_image:
			attr['background-image'] = background_image
		if background_repeat:
			attr['background-repeat'] = background_repeat
		if background_position:
			attr['background-position'] = background_position
		if background_size:
			attr['background-size'] = background_size

		return f"""
	    @page {page_selector} {{
	        {join_styles(attr)}
	        
	        @top-right {{
	            content: {f'"{top_right_content}"' if top_right_content else 'none'};
	        }}
	        	
	        @bottom-center {{
	            content: {f'"{bottom_center_content}"' if bottom_center_content != 'none' else 'none'}
	        }}
	    }}
	    """

	def first_page(
			self,
			):
		"""
		Generates the CSS for the first page background.
		"""
		return self.page(
			page_selector=self.FIRST_PAGE_SELECTOR,
			background_color=self.__page_background_color_first_page,
			)

	def section_page(
			self,
			page_selector: str,
			top_right_content: str,
			):
		"""
		Generates the CSS for a section page background.

		Args:
			page_selector (str): The CSS selector for the section page.
			top_right_content (str): Content for the top-right corner of the section page.
		"""
		return self.page(
			page_selector=page_selector,
			background_color=self.__page_background_color_section_page,
			top_right_content=top_right_content,
			bottom_center_content='none',
			#top_right_background_color=self.__page_background_color_section_page,
			#top_right_color=self.__font_color_h1_section,
			)

	def section_body(
			self,
			page_selector: str,
	        top_right_content: str
	    ) -> str:
		"""
		Generates the CSS for a section body.

		Args:
			page_selector (str): The CSS selector for the section body.
			top_right_content (str): Content for the top-right corner of the section body.
		"""
		return self.page(
			page_selector=page_selector,
			top_right_content=top_right_content,
			#top_right_background_color=self.__page_background_color_section_page,
			#top_right_color=self.__font_color_h1_section,
			)

	@property
	def stylesheet_file(self) -> str:
		"""
		Returns the path to the stylesheet file.
		"""
		return self.__stylesheet_file

	@property
	def font_size_h1_section(self) -> str:
		"""
		Returns the font size for H1 headers in sections.
		"""
		return self.__font_size_h1_section

	@property
	def font_color_h1_section(self) -> str:
		"""
		Returns the font color for H1 headers in sections.
		"""
		return self.__font_color_h1_section

	@property
	def font_family_sans_serif(self) -> str:
		"""
		Returns the font family for sans-serif text.
		"""
		return self.__font_family_sans_serif

	@property
	def font_family_monospace(self) -> str:
		"""
		Returns the font family for monospace text.
		"""
		return self.__font_family_monospace

	@property
	def page_format(self) -> str:
		"""
		Returns the page format for the PDF.
		"""
		return self.__page_format

	@property
	def page_height(self) -> Measure:
		"""
		Returns the height of the page based on the page format.
		"""
		return self.__page_height

	@property
	def page_background_color_first_page(self) -> str:
		"""
		Returns the background color for the first page.
		"""
		return self.__page_background_color_first_page

	@property
	def page_background_color_section_page(self) -> str:
		"""
		Returns the background color for section pages.
		"""
		return self.__page_background_color_section_page

	@property
	def page_margin(self) -> Measure:
		"""
		Returns the page margin for the PDF.
		"""
		return self.__page_margin