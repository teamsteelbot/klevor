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
STYLESHEET_DIR = os.path.join(PDF_DIR, 'stylesheets')
COMMON_STYLESHEET_FILE = os.path.join(STYLESHEET_DIR, 'common.css')
DIGITAL_STYLESHEET_FILE = os.path.join(STYLESHEET_DIR, 'digital.css')
PRINTING_STYLESHEET_FILE = os.path.join(STYLESHEET_DIR, 'printing.css')

# PDF output files flags
GENERATE_PRINTING_PDF = False
GENERATE_DIGITAL_PDF = True

# PDF output files
PRINTING_PDF_OUTPUT_FILE = os.path.join(DOWNLOADS_DIR, 'teamsteelbot--printing.pdf')
DIGITAL_PDF_OUTPUT_FILE = os.path.join(DOWNLOADS_DIR, 'teamsteelbot--digital.pdf')
PDF_OUTPUT_FILES = []
PDF_OUTPUT_FILES.append((PRINTING_PDF_OUTPUT_FILE, PRINTING_STYLESHEET_FILE)) if GENERATE_PRINTING_PDF else None
PDF_OUTPUT_FILES.append((DIGITAL_PDF_OUTPUT_FILE, DIGITAL_STYLESHEET_FILE)) if GENERATE_DIGITAL_PDF else None

# PDF DPI
PDF_DPI = 300

# Team logo file
TEAM_LOGO_FILE = os.path.join('assets', 'images', 'logo', 'teamsteelbot.png')

# First page HTML
FIRST_PAGE_HTML = f"""
    <div class="special-page">
        <img src="{TEAM_LOGO_FILE}" class="special-page-logo" alt="Team SteelBot Logo">
    </div>
    """

# Omitted MkDocs pages and directories
OMITTED_DIRECTORIES = [
	'programming/code',
	]
OMITTED_PAGES = [
	'sponsors.md',
	]

# Break page HTML
BREAK_PAGE_HTML = '\n<div class="page-break"></div>\n'
