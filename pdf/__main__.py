import os

from markdown import markdown
from bs4 import BeautifulSoup

from .constants import (
	DOCS_DIR, MAIN_INDEX_DB,
	)
from .yml import YAML
from .styles import Styles
from . import PDF

if __name__ == '__main__':
	# Initialize the styles
	styles = Styles()

	# Initialize the PDF
	pdf = PDF(styles)

	# Add the first page with the team logo
	team_logo_tag = pdf.team_logo()
	pdf.add_first_page(team_logo_tag)

	# Get the MarkDown files
	md_files = YAML.extract_md_paths_from_mkdocs()

	for idx, md_file in enumerate(md_files):
		# Get the Markdown file path and directory
		md_file_directory_path = os.path.dirname(md_file.path)
		md_file_path = os.path.join(DOCS_DIR, md_file.path)

		with (open(md_file_path, 'r', encoding='utf-8') as f):
			# Read the content of the Markdown file
			content = f.read()

			# Convert Markdown to HTML
			md_html_body = markdown(
				content,
				extensions=['tables', 'fenced_code', 'admonition'],
				)

			# Parse the HTML with BeautifulSoup
			soup = BeautifulSoup(md_html_body, 'html.parser')

			# Special parsing
			if md_file.path == MAIN_INDEX_DB:
				# Get the <h2> Index tag for the main index
				h2_tags = soup.find_all('h2')

				# Get only the tag contains {:#index} or {#index}
				index_tag = None
				for h2_tag in h2_tags:
					if '{:#index}' in h2_tag.get_text() or '{#index}' in h2_tag.get_text():
						index_tag = h2_tag
						break

				if not index_tag:
					raise RuntimeError(f'Markdown file {md_file.path} does not contain an <h2> tag for the index.')

				# Remove all the child of soup
				soup.clear()

				# Convert this tag to <h1> and added it to the soup
				h1_tag = soup.new_tag('h1', string=index_tag.string)
				soup.insert(0, h1_tag)

				# Move all tags next to the index_tag and before the next <h2> tag
				for sibling in index_tag.find_next_siblings():
					if sibling.name == 'h1' or sibling.name == 'h2':
						break
					soup.append(sibling.extract())

			# Iterate over all <img> tags to convert relative paths
			pdf.normalize_images_src(
				soup,
				lambda img_src: os.path.normpath(
					os.path.join(md_file_directory_path, img_src),
				)
			)

			# Iterate over all <h1> to <h6> tags to remove the ID from the header text
			pdf.normalize_headers_id(soup, md_file.path)

			# Get the depth and number of the current Markdown file
			number = [md_file.number]
			parent_dir = md_file.parent_dir
			while parent_dir is not None:
				number.insert(0, parent_dir.number)
				parent_dir = parent_dir.parent_dir
			full_number = '. '.join(map(str, number))

			# Check if it's the first from section
			if md_file.is_first_from_section():
				# Check if it's a top level file
				if md_file.is_top_level():
					# Get the <h1> tag for the title
					title_tag = soup.find('h1')
					if not title_tag:
						raise RuntimeError(f'Markdown file {md_file.path} does not contain an <h1> tag for the title.')
					title_tag_text = title_tag.get_text()

					# Remove the <h1> tag from the soup
					title_tag.decompose()

				# Add the title page
				title_tag = pdf.section_title(md_file.get_section_name())
				pdf.add_section_page(title_tag, full_number)

				# Create a new parent tag
				section_body_tag = soup.new_tag('div')

				# Move all children of soup into the parent
				for child in list(soup.contents):
					section_body_tag.append(child.extract())
			
			# Add the section body to the PDF
			pdf.add_section_body(section_body_tag, full_number)

	try:
		pdf.save()
	except Exception as e:
		print(f'Error saving PDF: {e}')
