import dataclasses
from typing import Optional

import yaml

import pymdownx.superfences

from .constants import MKDOCS_CONFIG_FILE

@dataclasses.dataclass
class MarkdownFile:
	"""
	Class representing a Markdown file.
	"""
	name: str
	path: str
	parent_dir: Optional[str] = None

@dataclasses.dataclass
class DocumentationDirectory:
	"""
	Class representing a documentation directory.
	"""
	name: str
	parent_dir: Optional['DocumentationDirectory'] = None
	depth: int = 0

def extract_md_paths(nav, documentation_dir=None):
	"""
	Extracts all Markdown file paths from the navigation structure.

	Args:
		nav (list): The navigation structure from mkdocs.yml.
	Returns:
		files (list): A list of MarkdownFile objects representing the Markdown files.
	"""
	if documentation_dir is None:
		documentation_dir = DocumentationDirectory(name='docs')

	# Iterate over the navigation structure
	files = []
	for item in nav:
		key, value = next(iter(item.items()))

		if isinstance(value, list):
			# Initialize a DocumentationDirectory object for the subdirectory
			sub_dir = DocumentationDirectory(name=key, parent_dir=documentation_dir, depth=documentation_dir.depth + 1)

			# Recursively extract paths from the subdirectory
			nested_files = extract_md_paths(value, sub_dir)
			files.extend(nested_files)

		elif isinstance(value, str) and value.endswith('.md'):
			# Initialize a MarkdownFile object for the Markdown file
			md_file = MarkdownFile(name=key, path=value, parent_dir=documentation_dir)
			files.append(md_file)
	return files

def extract_md_paths_from_yaml(yaml_file):
	"""
	Extracts Markdown file paths from a YAML file.

	Args:
		yaml_file (str): Path to the YAML file.
	Returns:
		list: A list of Markdown file paths.
	"""
	# Load the MkDocs configuration file
	with open(yaml_file, 'r', encoding='utf-8') as f:
		config = yaml.load(f, Loader=yaml.FullLoader)

	# Extract Markdown file paths from the navigation structure
	return extract_md_paths(config.get('nav', []))

if __name__ == '__main__':
	# Extract Markdown file paths from the MkDocs configuration file
	md_files = extract_md_paths_from_yaml(MKDOCS_CONFIG_FILE)
	print(md_files)