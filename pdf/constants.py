import os

# Root directory of the project
ROOT_DIR = os.path.abspath(
	os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'),
	)

# Assets directory
ASSETS_DIR = os.path.join(ROOT_DIR, 'assets')

# MkDocs docs folder
DOCS_DIR = os.path.join(ROOT_DIR, 'docs')

# MkDocs downloads folder
DOWNLOADS_DIR = os.path.join(DOCS_DIR, 'downloads')

# PDF directory
PDF_DIR = os.path.join(ROOT_DIR, 'pdf')

# Omitted MkDocs pages and directories
OMITTED_DIRECTORIES = [
	'programming/code',
	]
OMITTED_PAGES = [
	'sponsors.md',
	]