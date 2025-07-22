import os

from markdown import markdown
from weasyprint import HTML, CSS
from bs4 import BeautifulSoup

from .constants import (
	DOCS_DIR,
	COMMON_STYLESHEET_FILE,
	DIGITAL_STYLESHEET_FILE,
	PRINTING_STYLESHEET_FILE,
	MKDOCS_CONFIG_FILE,
	FIRST_PAGE_HTML,
	BREAK_PAGE_HTML,
	PRINTING_PDF_OUTPUT_FILE,
	DIGITAL_PDF_OUTPUT_FILE,
	PDF_DPI, PDF_OUTPUT_FILES,
	)
from .yml import extract_md_paths_from_yaml

if __name__ == '__main__':
	# Get the MarkDown files
	md_files = extract_md_paths_from_yaml(MKDOCS_CONFIG_FILE)

	# Add first page with title
	html_body = FIRST_PAGE_HTML
	html_body += BREAK_PAGE_HTML

	# Iterate over the files and directories in the docs directory
	for idx, md_file in enumerate(md_files):
		md_file_directory_path = os.path.dirname(md_file.path)
		md_file_path = os.path.join(DOCS_DIR, md_file.path)
		with open(md_file_path, 'r', encoding='utf-8') as f:
			content = f.read()

			# Convert Markdown to HTML
			md_html_body = markdown(
				content,
				extensions=['tables', 'fenced_code', 'admonition'],
				)

			# Parse the HTML with BeautifulSoup
			soup = BeautifulSoup(md_html_body, 'html.parser')

			# Iterate over all <img> tags to convert relative paths
			images = soup.find_all('img')
			for img in images:
				img_src = img.get('src')
				if img_src and not img_src.startswith(('http://', 'https://')):
					# Convert relative image paths
					img_src = os.path.normpath(
						os.path.join(md_file_directory_path, img_src),
						)
					img['src'] = img_src

			# Iterate over all <h1> to <h6> tags to remove the ID
			headers = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
			for header in headers:
				# Remove the {:#id} part from the header text
				header_text = header.get_text()
				if '{:#' in header_text:
					header_text = header_text.split('{:#')[0].strip()
					header.string = header_text

			html_body += str(soup)
			if idx < len(md_files) - 1:
				# Add a page break after each file except the last one
				html_body += BREAK_PAGE_HTML

	try:
		html = f"""
			<html>
				<body>
					{html_body}
				</body>
			</html>
		"""
		for path, stylesheet in PDF_OUTPUT_FILES:
			print (f'Saving PDF to {path}...')
			if not os.path.exists(os.path.dirname(path)):
				os.makedirs(os.path.dirname(path))
			HTML(string=html, base_url=DOCS_DIR).write_pdf(
				path,
				stylesheets=[
					CSS(COMMON_STYLESHEET_FILE),
					CSS(stylesheet)
				],
				optimize_images=True,
				dpi=PDF_DPI,
				)
			print(f'PDF saved to {path}')
	except Exception as e:
		print(f'Error saving PDF: {e}')
