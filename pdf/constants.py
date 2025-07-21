import os

# Root directory of the project
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

# MkDocs configuration file
MKDOCS_CONFIG_FILE = os.path.join(ROOT_DIR, 'mkdocs.yml')

# MkDocs docs folder
DOCS_DIR = os.path.join(ROOT_DIR, 'docs')

# PDF directory
PDF_DIR = os.path.join(ROOT_DIR, 'pdf')

# PDF output file
PDF_OUTPUT_FILE = os.path.join(DOCS_DIR, 'downloads', 'teamsteelbot.pdf')

# WeasyPrint stylesheet file
STYLESHEET_FILE = os.path.join(PDF_DIR, 'styles.css')

# Team logo file
TEAM_LOGO_FILE = os.path.join('assets', 'images', 'logo', 'teamsteelbot.png')

# First page HTML
FIRST_PAGE_HTML = f"""
    <div class="first-page">
        <img src="{TEAM_LOGO_FILE}" class="first-page-logo" alt="Team SteelBot Logo">
    </div>
    """

# Omitted MkDocs pages and directories
OMITTED_DIRECTORIES = [
	'programming/code'
]
OMITTED_PAGES = [
	'sponsors.md',
]

# Break page HTML
BREAK_PAGE_HTML = '\n<div class="page-break"></div>\n'