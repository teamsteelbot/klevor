class HTML:
	"""
	A class to handle HTML generation for WeasyPrint and that also provides
	the constant HTML elements used in the PDF generation.
	"""

	# Empty div element
	EMPTY_DIV_HTML = '<div></div>\n'

	# Break page HTML
	BREAK_PAGE_HTML = '<div class="page-break"></div>\n'