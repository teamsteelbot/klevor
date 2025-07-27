class Measure:
	"""
	A class to represent a measure in a PDF document.
	"""

	# Valid units for measurements
	INCH_UNIT = 'in'
	CM_UNIT = 'cm'
	MM_UNIT = 'mm'
	PT_UNIT = 'pt'

	@staticmethod
	def is_valid_unit(unit: str) -> bool:
		"""
		Checks if the provided unit is a valid measurement unit.

		Args:
			unit (str): The unit to check.

		Returns:
			bool: True if the unit is valid, False otherwise.
		"""
		return unit in {Measure.INCH_UNIT, Measure.CM_UNIT, Measure.MM_UNIT, Measure.PT_UNIT}

	@staticmethod
	def parse_style_measure(
			style: str,
			) -> 'Measure':
		"""
		Parses a style string and returns a Measure object.

		Args:
			style (str): The style string to parse.
		Returns:
			Measure: A Measure object representing the parsed style.
		"""
		# Convert the style string to a Measure object
		value = float(style[:-2])
		unit = style[-2:]  # Get the last two characters as the unit
		return Measure(value, unit)

	@staticmethod
	def convert(value: float, from_unit: str, to_unit: str) -> float:
		"""
		Converts a value from one unit to another.

		Args:
			value (float): The numeric value to convert.
			from_unit (str): The unit of the value.
			to_unit (str): The unit to convert to.

		Returns:
			float: The converted value in the target unit.
		"""
		if not Measure.is_valid_unit(from_unit) or not Measure.is_valid_unit(to_unit):
			raise ValueError(f"Invalid units: {from_unit}, {to_unit}. Valid units are: {Measure.INCH_UNIT}, {Measure.CM_UNIT}, {Measure.MM_UNIT}, {Measure.PT_UNIT}.")

		# Check if the conversion is necessary
		if from_unit == to_unit:
			return value

		# Conversion factors for each unit
		if from_unit == Measure.INCH_UNIT:
			if to_unit == Measure.CM_UNIT:
				return value * 2.54
			if to_unit == Measure.MM_UNIT:
				return value * 25.4
			if to_unit == Measure.PT_UNIT:
				return value * 72.0
		elif from_unit == Measure.CM_UNIT:
			if to_unit == Measure.INCH_UNIT:
				return value / 2.54
			if to_unit == Measure.MM_UNIT:
				return value * 10.0
			if to_unit == Measure.PT_UNIT:
				return value * 72.0 / 2.54
		elif from_unit == Measure.MM_UNIT:
			if to_unit == Measure.INCH_UNIT:
				return value / 25.4
			if to_unit == Measure.CM_UNIT:
				return value / 10.0
			if to_unit == Measure.PT_UNIT:
				return value * 72.0 / 25.4
		elif from_unit == Measure.PT_UNIT:
			if to_unit == Measure.INCH_UNIT:
				return value / 72.0
			if to_unit == Measure.CM_UNIT:
				return value * 2.54 / 72.0
			if to_unit == Measure.MM_UNIT:
				return value * 25.4 / 72.0

		raise ValueError(f"Conversion from {from_unit} to {to_unit} is not supported.")


	def __init__(self, value: float, unit: str = PT_UNIT):
		"""
		Initializes a Measure instance with a value and unit.

		Args:
			value (float): The numeric value of the measure.
			unit (str): The unit of the measure.
		"""
		# Check if the unit is valid
		if not Measure.is_valid_unit(unit):
			raise ValueError(f"Invalid unit: {unit}. Valid units are: {Measure.INCH_UNIT}, {Measure.CM_UNIT}, {Measure.MM_UNIT}, {Measure.PT_UNIT}.")

		self.value = value
		self.unit = unit

	def __str__(self) -> str:
		"""
		Returns a string representation of the measure.
		"""
		return f"{self.value}{self.unit}"

	def __add__(self, other: 'Measure') -> 'Measure':
		other_converted = other.to_unit(self.unit)
		return Measure(self.value + other_converted.value, self.unit)

	def __sub__(self, other: 'Measure') -> 'Measure':
		other_converted = other.to_unit(self.unit)
		return Measure(self.value - other_converted.value, self.unit)

	def to_unit(self, target_unit: str) -> 'Measure':
		"""
		Converts the measure to a specified unit.

		Args:
			target_unit (str): The unit to convert the measure to.

		Returns:
			Measure: A new Measure instance with the converted value and target unit.
		"""
		if not Measure.is_valid_unit(target_unit):
			raise ValueError(f"Invalid target unit: {target_unit}. Valid units are: {Measure.INCH_UNIT}, {Measure.CM_UNIT}, {Measure.MM_UNIT}, {Measure.PT_UNIT}.")

		converted_value = Measure.convert(self.value, self.unit, target_unit)
		return Measure(converted_value, target_unit)

