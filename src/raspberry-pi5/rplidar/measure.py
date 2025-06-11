from utils import check_type

class Measure:
    """
    Represents a single measurement from the RPLIDAR.
    """
    # Attributes separator
    ATTRIBUTES_SEPARATOR = ","

    # Measures separator
    MEASURES_SEPARATOR = ";"

    def __init__(self, angle: float, distance: float, quality: int):
        """
        Initialize the Measure instance.
        """
        self.angle = angle
        self.distance = distance
        self.quality = quality

    def __str__(self):
        """
        String representation of the Measure object.
        """
        return self.ATTRIBUTES_SEPARATOR.join([str(self.angle), str(self.distance), str(self.quality)])
        #return self.ATTRIBUTES_SEPARATOR.join([str(self.angle), str(self.distance)])

    def __repr__(self):
        """
        String representation of the Measure object for debugging.
        """
        return f"Measure(angle={self.angle}, distance={self.distance}, quality={self.quality})"
    
    @property
    def angle(self) -> float:
        """
        Get the angle of the measure.
        
        Returns:
            float: Angle of the measure.
        """
        return self.__angle
    
    @angle.setter
    def angle(self, value: float) -> None:
        """
        Set the angle of the measure.
        
        Args:
            value (float): Angle to set.
        """
        check_type(value, float)

        if not (0 <= value):
            raise ValueError("Angle must be a non-negative float, received: {}".format(value))
        self.__angle = 360.0 if value > 360.0 else value

    @property
    def distance(self) -> float:
        """
        Get the distance of the measure.
        
        Returns:
            float: Distance of the measure.
        """
        return self.__distance
    
    @distance.setter
    def distance(self, value: float) -> None:
        """
        Set the distance of the measure.
        
        Args:
            value (float): Distance to set.
        """
        check_type(value, float)

        if value < 0:
            raise ValueError("Distance must be a non-negative float, received: {}".format(value))
        
        self.__distance = value

    @property
    def quality(self) -> int:
        """
        Get the quality of the measure.
        
        Returns:
            int: Quality of the measure.
        """
        return self.__quality
    
    @quality.setter
    def quality(self, value: int) -> None:
        """
        Set the quality of the measure.
        
        Args:
            value (int): Quality to set.
        """
        check_type(value, int)
        self.__quality = value

    @classmethod
    def from_string(cls, measure_str: str) -> 'Measure':
        """
        Create a Measure object from a string representation.

        Args:
            measure_str (str): String representation of the measure.

        Returns:
            Measure: Measure object created from the string.
        """
        # Check the type of measure_str
        check_type(measure_str, str)

        # Split the string by the attributes separator
        parts = measure_str.split(cls.ATTRIBUTES_SEPARATOR)

        if len(parts) < 2:
            raise ValueError("Invalid measure string: {}".format(measure_str))

        # Convert parts to appropriate types
        angle = float(parts[0])
        distance = float(parts[1])

        # Quality is optional, default to 0 if not provided
        quality = int(parts[2]) if len(parts) > 2 else 0

        return cls(angle, distance, quality)
    
    @classmethod
    def measures_to_string(cls, measures: list) -> str:
        """
        Convert a list of Measure objects to a string representation.
        
        Args:
            measures (list): List of Measure objects.
        
        Returns:
            str: String representation of the measures.
        """
        # Check the type of measures
        check_type(measures, list)
        
        # Convert each measure to string and join them with spaces
        return cls.MEASURES_SEPARATOR.join(str(measure) for measure in measures)

    @classmethod
    def from_string_to_measures(cls, measures_str: str) -> list:
        """
        Convert a string representation of measures back to a list of Measure objects.

        Args:
            measures_str (str): String representation of measures.

        Returns:
            list: List of Measure objects.
        """
        # Check the type of measures_str
        check_type(measures_str, str)

        # Split the string by the measures separator and convert each part to Measure
        return [cls.from_string(measure_str) for measure_str in measures_str.split(cls.MEASURES_SEPARATOR) if measure_str]