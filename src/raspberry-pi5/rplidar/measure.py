from utils import check_type

class Measure:
    """
    Represents a single measurement from the RPLIDAR.
    """
    def __init__(self, angle: float, distance: float, quality: int):
        """
        Initialize the Measure instance.
        """
        self.angle = angle
        self.distance = distance
        self.quality = quality

    def __repr__(self):
        return f"{self.angle},{self.distance},{self.quality}"
    
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

        if not (0 <= value <= 360):
            raise ValueError("Angle must be between 0 and 360 degrees, received: {}".format(value))

        self.__angle = value

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
        return ";".join(str(measure) for measure in measures)