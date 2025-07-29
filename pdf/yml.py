import dataclasses
from typing import Optional
import os

import yaml

import pymdownx.superfences

from .constants import (
	OMITTED_DIRECTORIES,
	OMITTED_PAGES, ROOT_DIR,
	)


@dataclasses.dataclass
class MarkdownFile:
	"""
	Class representing a Markdown file.
	"""
	name: str
	path: str
	parent_dir: Optional['DocumentationSection'] = None
	number: int = 0

	def is_top_level(self):
		return self.parent_dir is None

	def is_first_from_section(self):
		"""
		Check if this Markdown file is the first file in its section.

		Returns:
			bool: True if this is the first file in its section, False otherwise.
		"""
		return self.is_top_level() or (self.number == 1 and self.parent_dir.is_first_from_section())

	def get_section_name(self) -> str:
		"""
		Get the name of the section, including its parent directories.

		Returns:
			str: The full name of the section.
		"""
		if self.parent_dir is None:
			return self.name
		return self.parent_dir.get_section_name()

@dataclasses.dataclass
class DocumentationSection:
	"""
	Class representing a documentation section.
	"""
	name: str
	parent_dir: Optional['DocumentationSection'] = None
	depth: int = 0
	number: int = 0

	def is_first_from_section(self):
		"""
		Check if this section is the first section in its parent directory.

		Returns:
			bool: True if this is the first section in its parent directory, False otherwise.
		"""
		return self.depth == 1 or (self.number == 1 and self.parent_dir.is_first_from_section())

	def get_section_name(self) -> str:
		"""
		Get the name of the section, including its parent directories.

		Returns:
			str: The full name of the section.
		"""
		if self.parent_dir is None:
			return self.name
		return self.parent_dir.get_section_name()

class YAML:
	"""
	Class for handling YAML files.
	"""

	# MkDocs configuration file
	MKDOCS_CONFIG_FILE = os.path.join(ROOT_DIR, 'mkdocs.yml')

	@staticmethod
	def load_yaml(yaml_file: str) -> dict:
		"""
		Load a YAML file and return its content.

		Args:
			yaml_file (str): Path to the YAML file.
		Returns:
			dict: The content of the YAML file.
		"""
		# Check if the file exists
		if not os.path.exists(yaml_file):
			raise FileNotFoundError(f"YAML file '{yaml_file}' not found.")

		# Load the MkDocs configuration file
		with open(yaml_file, 'r', encoding='utf-8') as f:
			return yaml.load(f, Loader=yaml.FullLoader)

	@staticmethod
	def extract_md_paths_from_mkdocs_nav(nav, documentation_section = None) -> list[MarkdownFile]:
		"""
		Extracts all Markdown file paths from the navigation structure in mkdocs.yml.

		Args:
			nav (list): The navigation structure from mkdocs.yml.
			documentation_section (DocumentationSection, optional): The parent documentation section. If None, a new DocumentationSection with an empty name is created.
		Returns:
			A list of MarkdownFile objects representing the Markdown files.
		"""
		# Iterate over the navigation structure
		files = []
		for idx, item in enumerate(nav):
			key, value = next(iter(item.items()))

			if isinstance(value, list):
				# Initialize a DocumentationSection object for the subdirectory
				sub_dir = DocumentationSection(
					name=key,
					parent_dir=documentation_section,
					depth=documentation_section.depth + 1 if documentation_section else 0,
					number=idx + 1,
					)

				# Recursively extract paths from the subdirectory
				nested_files = YAML.extract_md_paths_from_mkdocs_nav(value, sub_dir)
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
				if idx == 0 and documentation_section is None:
					key = 'Índice'
				md_file = MarkdownFile(
					name=key,
					path=value,
					parent_dir=documentation_section,
					number=idx + 1,
					)
				files.append(md_file)
		return files

	@staticmethod
	def extract_md_paths_from_mkdocs(yaml_file = MKDOCS_CONFIG_FILE) -> list[MarkdownFile]:
		"""
		Extracts Markdown file paths from the MkDocs configuration file.

		Args:
			yaml_file (str): Path to the MkDocs configuration file (mkdocs.yml).
		Returns:
			list: A list of Markdown file paths.
		"""
		# Load the MkDocs configuration file
		config = YAML.load_yaml(yaml_file)

		# Extract Markdown file paths from the navigation structure
		return YAML.extract_md_paths_from_mkdocs_nav(config.get('nav', []))


if __name__ == '__main__':
	# Extract Markdown file paths from the MkDocs configuration file
	md_files = YAML.extract_md_paths_from_mkdocs()
	print(md_files)
