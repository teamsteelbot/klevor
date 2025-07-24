class Styles:
	"""
	Styles class for generating CSS styles for WeasyPrint and that also
	provides the constant styles used in the PDF generation.
	"""

	# Custom styles
	FONT_SIZE_H1 = '36pt'
	FONT_COLOR_H1 = '#fff'
	PAGE_BACKGROUND_COLOR_FIRST_PAGE = '#fac319'
	PAGE_BACKGROUND_COLOR_SECTION_PAGE = '#212529'

	@staticmethod
	def page_background(
			background_color: str,
			background_image: str,
			page_idx: int = 0,
	        background_repeat: str  ='no-repeat',
			background_position: str = 'center center',
	        content: str = 'none') -> str:
		"""
	    Generates CSS for a specific page of a PDF document with a specified background.
	
	    Args:
			background_color (str): The background color for the page.
			background_image (str): The background image for the page, formatted as a CSS URL.
	        page_idx (int): The page number to apply the CSS to (0-based index).
	        background_repeat (str): The repeat style for the background image.
	        background_position (str): The position of the background image.
	        content (str): The content to display at the bottom center of the page.
	    Returns:
	        str: The complete CSS string for the specified page.
	    """
		return f"""
	    @page :nth({page_idx + 1}) {{
	        background: {background_color} {background_image} {background_repeat} {background_position};
	
	        @bottom-center {{
	            content: {content};
	        }}
	    }}
	    """