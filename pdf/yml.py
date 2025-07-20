import dataclasses
from typing import Optional

import yaml

import pymdownx.superfences

from .constants import (
	MKDOCS_CONFIG_FILE,
	ROOT_DIR,
	OMITTED_DIRECTORIES,
	OMITTED_PAGES,
	)


@dataclasses.dataclass
class MarkdownFile:
	"""
	Class representing a Markdown file.
	"""
	name: str
	path: str
	parent_dir: Optional[str] = None

@dataclasses.dataclass
class DocumentationSection:
	"""
	Class representing a documentation section.
	"""
	name: str
	parent_dir: Optional['DocumentationSection'] = None
	depth: int = 0

def extract_md_paths(nav, documentation_section=None) -> list[MarkdownFile]:
	"""
	Extracts all Markdown file paths from the navigation structure.

	Args:
		nav (list): The navigation structure from mkdocs.yml.
		documentation_section (DocumentationSection, optional): The parent documentation section. If None, a new DocumentationSection with an empty name is created.
	Returns:
		A list of MarkdownFile objects representing the Markdown files.
	"""
	if documentation_section is None:
		documentation_section = DocumentationSection(name='')

	# Iterate over the navigation structure
	files = []
	for item in nav:
		key, value = next(iter(item.items()))

		if isinstance(value, list):
			# Initialize a DocumentationSection object for the subdirectory
			sub_dir = DocumentationSection(name=key, parent_dir=documentation_section, depth=documentation_section.depth + 1)

			# Recursively extract paths from the subdirectory
			nested_files = extract_md_paths(value, sub_dir)
			files.extend(nested_files)

		elif isinstance(value, str) and value.endswith('.md'):
			# Check if the file is inside an omitted directory
			skip_file = False
			for omitted_dir in OMITTED_DIRECTORIES:
				if value.startswith(omitted_dir):
					skip_file = True
					break
			if skip_file:
				continue

			# Check if the file is an omitted page
			for omitted_page in OMITTED_PAGES:
				if value.endswith(omitted_page):
					skip_file = True
					break
			if skip_file:
				continue

			# Initialize a MarkdownFile object for the Markdown file
			md_file = MarkdownFile(name=key, path=value, parent_dir=documentation_section)
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