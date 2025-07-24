class HTML:
	"""
	A class to handle HTML generation for WeasyPrint and that also provides
	the constant HTML elements used in the PDF generation.
	"""

	# Empty div element
	EMPTY_DIV_HTML = '<div></div>\n'

	# Break page HTML
	BREAK_PAGE_HTML = '<div class="page-break"></div>\n'

	@staticmethod
	def empty_div_with_page_selector(page_selector: str) -> str:
		"""
		Generates an empty div with a specific page selector for WeasyPrint.

		Args:
			page_selector (str): The CSS selector for the page.
		Returns:
			str: An empty div with the specified page selector.
		"""
		return f'<div style="page: {page_selector};"></div>\n'