import os

from markdown import markdown
from bs4 import BeautifulSoup

from .constants import (
	DOCS_DIR,
	)
from .yml import YAML
from .styles import Styles
from .svg import SVG
from . import PDF

if __name__ == '__main__':
	# Initialize the PDF
	pdf = PDF()

	# Initialize the styles
	styles = Styles()

	# Add the first page with the team logo
	team_logo = pdf.team_logo()
	first_page_selector = 'first'
	first_page_html = HTML.div_with_page_selector(first_page_selector, team_logo)
	first_page_styles = Styles.page_background(
		Styles.PAGE_BACKGROUND_COLOR_FIRST_PAGE,
		f'url("{SVG.FIRST_PAGE_SVG}")',
		page_selector=first_page_selector,
		)
	pdf.add_title_page(first_page_html, custom_styles=first_page_styles)

	# Get the MarkDown files
	md_files = YAML.extract_md_paths_from_mkdocs()

	for idx, md_file in enumerate(md_files):
		# Get the Markdown file path and directory
		md_file_directory_path = os.path.dirname(md_file.path)
		md_file_path = os.path.join(DOCS_DIR, md_file.path)

		with open(md_file_path, 'r', encoding='utf-8') as f:
			# Read the content of the Markdown file
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

			# Iterate over all <h1> to <h6> tags to remove the ID from the header text
			headers = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
			for header in headers:
				# Remove the {:#id} part from the header text
				header_text = header.get_text()
				if '{:#' in header_text:
					header_text = header_text.split('{:#')[0].strip()
					header.string = header_text

			# Get the <h1> tag for the title
			title_tag = soup.find('h1')
			if not title_tag:
				raise RuntimeError(f'Markdown file {md_file.path} does not contain an <h1> tag for the title.')
			title_tag_text = title_tag.get_text()

			# Remove the <h1> tag from the soup
			title_tag.decompose()

			# Get the depth and number of the current Markdown file
			number = [md_file.number]
			parent_dir = md_file.parent_dir
			while parent_dir is not None:
				number.insert(0, parent_dir.number)
				parent_dir = parent_dir.parent_dir
			full_number = '. '.join(map(str, number))

			# Add the title page
			page_selector = f'section-{idx + 1}'
			section_html = HTML.empty_div_with_page_selector(page_selector)
			background_svg = SVG.background_text(
				text=f"{full_number} {title_tag_text}",
				fill=Styles.FONT_COLOR_H1,
				font_size=Styles.FONT_SIZE_H1,
			)
			section_page_styles = Styles.page_background(
				Styles.PAGE_BACKGROUND_COLOR_SECTION_PAGE,
				background_svg,
				page_selector=page_selector,
				)
			pdf.add_title_page(section_html, custom_styles=section_page_styles)

			"""
			# Create a new parent tag
			parent = soup.new_tag('div', attrs={'class': 'wrapper'})
			
			# Move all children of soup into the parent
			for child in list(soup.contents):
			    parent.append(child.extract())
			
			# Replace soup's contents with the parent
			soup.clear()
			soup.append(parent)
			"""

			# Add a page break after each file except the last one
			pdf.add_html_content(str(soup), break_page=False)

	try:
		pdf.save()
	except Exception as e:
		print(f'Error saving PDF: {e}')
