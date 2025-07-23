import os

# Root directory of the project
ROOT_DIR = os.path.abspath(
	os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'),
	)

# MkDocs configuration file
MKDOCS_CONFIG_FILE = os.path.join(ROOT_DIR, 'mkdocs.yml')

# MkDocs docs folder
DOCS_DIR = os.path.join(ROOT_DIR, 'docs')

# MkDocs downloads folder
DOWNLOADS_DIR = os.path.join(DOCS_DIR, 'downloads')

# PDF directory
PDF_DIR = os.path.join(ROOT_DIR, 'pdf')

# WeasyPrint stylesheet files
STYLESHEET_FILE = os.path.join(PDF_DIR, 'styles.css')

# PDF output file
PDF_OUTPUT_FILE = os.path.join(DOWNLOADS_DIR, 'teamsteelbot.pdf')

# PDF DPI
PDF_DPI = 300

# Team logo file
TEAM_LOGO_FILE = os.path.join('assets', 'images', 'logo', 'teamsteelbot.png')

# Omitted MkDocs pages and directories
OMITTED_DIRECTORIES = [
	'programming/code',
	]
OMITTED_PAGES = [
	'sponsors.md',
	]

# Break page HTML
BREAK_PAGE_HTML = '\n<div class="page-break"></div>\n'
