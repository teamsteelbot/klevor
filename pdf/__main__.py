import os

from markdown import markdown
from weasyprint import HTML, CSS
from bs4 import BeautifulSoup

from .constants import (
	DOCS_DIR,
	MKDOCS_CONFIG_FILE,
	BREAK_PAGE_HTML,
	PDF_OUTPUT_FILE, STYLESHEET_FILE, PDF_DPI,
	)
from .yml import extract_md_paths_from_yaml

if __name__ == '__main__':
	# Get the MarkDown files
	md_files = extract_md_paths_from_yaml(MKDOCS_CONFIG_FILE)

	# Add first page with title
	html_body = "<div></div>"
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
		print (f'Saving PDF to {PDF_OUTPUT_FILE}...')
		if not os.path.exists(os.path.dirname(PDF_OUTPUT_FILE)):
			os.makedirs(os.path.dirname(PDF_OUTPUT_FILE))
		HTML(string=html, base_url=DOCS_DIR).write_pdf(
			PDF_OUTPUT_FILE,
			stylesheets=[
				CSS(STYLESHEET_FILE),
			],
			optimize_images=True,
			dpi=PDF_DPI,
		)
		print(f'PDF saved to {PDF_OUTPUT_FILE}')
	except Exception as e:
		print(f'Error saving PDF: {e}')
