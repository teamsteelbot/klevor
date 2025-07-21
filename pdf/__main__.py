import os

from markdown import markdown
from weasyprint import HTML, CSS
from bs4 import BeautifulSoup

from .constants import (
	DOCS_DIR,
	STYLESHEET_FILE,
	MKDOCS_CONFIG_FILE,
	FIRST_PAGE_HTML,
	BREAK_PAGE_HTML,
	)
from .yml import extract_md_paths_from_yaml

if __name__ == '__main__':
    # Get the MarkDown files
    md_files = extract_md_paths_from_yaml(MKDOCS_CONFIG_FILE)

    # Add first page with title
    html_body = FIRST_PAGE_HTML
    html_body += BREAK_PAGE_HTML

    # Iterate over the files and directories in the docs directory
    for md_file in md_files:
        md_file_directory_path = os.path.dirname(md_file.path)
        md_file_path = os.path.join(DOCS_DIR, md_file.path)
        with open(md_file_path, 'r', encoding='utf-8') as f:
            content = f.read()

            # Convert Markdown to HTML
            md_html_body = markdown(content, extensions=['tables', 'fenced_code', 'admonition'])

            # Parse the HTML with BeautifulSoup
            soup = BeautifulSoup(md_html_body, 'html.parser')

            # Extract the images
            images = soup.find_all('img')

            for img in images:
                img_src = img.get('src')
                if img_src and not img_src.startswith(('http://', 'https://')):
                    # Convert relative image paths
                    img_src = os.path.normpath(os.path.join(md_file_directory_path, img_src))
                    print(f'Converting image path: {img_src}')
                    img['src'] = img_src

            html_body += str(soup)
            html_body += BREAK_PAGE_HTML

    output_pdf = os.path.join(DOCS_DIR, 'html.pdf')
    try:
        print(f'Saving PDF to {output_pdf}...')
        html =  f"""
			<html>
				<body>
					{html_body}
				</body>
			</html>
		"""
        HTML(string=html, base_url=DOCS_DIR).write_pdf(output_pdf, stylesheets=[CSS(STYLESHEET_FILE)])
        print(f'PDF saved to {output_pdf}')
    except Exception as e:
        print(f'Error saving PDF: {e}')
