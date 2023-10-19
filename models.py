from dataclasses import dataclass

@dataclass
class Point:
    """
    Class to represent a point on the earth's surface

    Attributes:
        latitude: float
        longitude: float
    """

    latitude: float
    longitude: float

@dataclass
class Library:
    """
    Class to represent a library

    Attributes:
        name: str
        point: Point
    """

    name: str
    point: Point

@dataclass
class DistancedLibrary(Library):
    """
    Class to represent a library with a distance

    Attributes:
        name: str
        point: Point
        distance: float
    """

    distance: float