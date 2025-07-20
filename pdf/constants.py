import os

# Root directory of the project
ROOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

# MkDocs configuration file
MKDOCS_CONFIG_FILE = os.path.join(ROOT_DIR, 'mkdocs.yml')

# MkDocs docs folder
DOCS_DIR = os.path.join(ROOT_DIR, 'docs')

# WeasyPrint stylesheet file
STYLESHEET_FILE = os.path.join(ROOT_DIR, 'styles.css')
