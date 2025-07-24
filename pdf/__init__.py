import os

from weasyprint import HTML as WeasyPrintHTML, CSS

from .html import HTML
from .constants import (
	PDF_DIR,
	DOWNLOADS_DIR,
    DOCS_DIR
	)

class PDF:
	"""
	A class to handle PDF generation for WeasyPrint
	"""

	# WeasyPrint stylesheet files
	STYLESHEET_FILE = os.path.join(PDF_DIR, 'styles.css')

	# PDF output file
	PDF_OUTPUT_FILE = os.path.join(DOWNLOADS_DIR, 'teamsteelbot.pdf')

	# PDF DPI
	PDF_DPI = 300

	# PDF base URL
	PDF_BASE_URL = DOCS_DIR

	def __init__(self):
		# Initialize any necessary attributes or configurations here
		self.__html_body = ''
		self.__styles_files = []
		self.__custom_styles = []

	def add_title_page(
			self,
			html_content: str = '',
			custom_styles: str = '',
			break_page: bool = True):
		"""
		Adds a title page to the PDF document.

		Args:
			html_content (str): The HTML content for the title page.
			custom_styles (str): Custom CSS styles to apply to the title page.
			break_page (bool): Whether to insert a page break after the title page.
		"""
		if not html_content:
			html_content = HTML.EMPTY_DIV_HTML
		self.add_html_content(html_content, break_page=break_page)

		if custom_styles:
			self.__custom_styles.append(custom_styles)

	def add_html_content(self, html_content: str, break_page: bool = True):
		"""
		Adds HTML content to the PDF document.

		Args:
			html_content (str): The HTML content to add.
			break_page (bool): Whether to insert a page break after the content.
		"""
		self.__html_body += html_content
		if break_page:
			self.__html_body += HTML.BREAK_PAGE_HTML

	def save(
			self,
			base_url: str = PDF_BASE_URL,
			output_file: str = PDF_OUTPUT_FILE,
			stylesheet: str = STYLESHEET_FILE,
			optimize_images: bool = True,
			dpi: int = PDF_DPI
		):
		"""
		Saves the PDF document to the specified output file.

		Args:
			base_url (str): The base URL for the HTML content.
			output_file (str): The path to the output PDF file.
			stylesheet (str): The stylesheet for the HTML content.
			optimize_images (bool): Whether to optimize images in the PDF.
			dpi (int): The DPI for the PDF output.
		"""

		# Check if the output file is a valid path
		if not os.path.exists(os.path.dirname(output_file)):
			os.makedirs(os.path.dirname(output_file))

		# Generate the PDF from the HTML content
		print(f'Saving PDF to {output_file}...')
		WeasyPrintHTML(
			string=f"""
				<html>
					<body>
						{self.__html_body}
					</body>
				</html>
				""",
			base_url=base_url
		).write_pdf(
			output_file=output_file,
			stylesheets=[
				CSS(stylesheet),
				],
			optimize_images=optimize_images,
			dpi=dpi,
			)
		print(f'PDF saved to {output_file}')