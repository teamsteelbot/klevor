from functools import singledispatch

@singledispatch
def join_styles(styles):
	raise TypeError(f"Unsupported type: {type(styles)}.")

@join_styles.register
def _(styles: dict) -> str:
	"""
	Joins a dictionary of styles into a CSS string.

	Args:
		styles (dict): A dictionary where keys are CSS properties and values are their corresponding values.

	Returns:
		str: A string representing the CSS styles.
	"""
	return '; '.join(f'{k}: {v}' for k, v in styles.items() if v is not None) + ';' if styles else ''