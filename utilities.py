# Standard Library Imports
import datetime

# Stand Library From Imports
from math import acos, sin, cos, radians

# Custom Imports
import constants

# Custom From Imports
from models import Point, Library, DistancedLibrary

def get_query_from_file(filename: str) -> str:
    """
    Gets a query from a file

    Parameters:
        filename (str): the name of the file to get the query from
    Returns:
        str - the query
    """

    with open(filename) as f:
        return f.read()

def check_date_older_than_days(date: datetime.date, days: int) -> bool:
    """
    Checks if a date is older than a given number of days

    Parameters:
        date (datetime.date): the date to check
        days (int): the number of days
    Returns:
        bool - True if the date is older than the number of days, False otherwise
    """

    return (datetime.date.today() - date) > datetime.timedelta(days=days)

def distance_between_points(point1: Point, point2: Point) -> float:
    """
    Calculates the distance between two points in kilometres

    Parameters:
        point1 (Point): the first point
        point2 (Point): the second point
    Returns:
        float - the distance between the two points in kilometres
    """
    
    return acos(
            sin(radians(point1.latitude)) * sin(radians(point2.latitude)) +
            cos(radians(point1.latitude)) * cos(radians(point2.latitude)) *
            cos(radians(point2.longitude) - radians(point1.longitude))
        ) * constants.EARTH_RADIUS_KM

def is_valid_integer(value: str) -> bool:
    """
    Checks if a string is an integer

    Parameters:
        value (str): the string to check
    Returns:
        bool - True if the string is an integer, False otherwise
    """
    
    try:
        int(value)
        return True
    except ValueError:
        return False

def find_nearest_n_libraries(libraries: list[Library], point: Point, n: int) -> list[Library]:
    """
    Finds the nearest n libraries to a point

    Parameters:
        libraries (list[Library]): the libraries to search
        point (Point): the point to find the nearest libraries to
        n (int): the number of libraries to find
    Returns:
        list[Library] - the nearest n libraries to the point.
    """

    if n <= 0:
        return []
    
    if len(libraries) <= n:
        return libraries
        
    distanced_libraries: list[DistancedLibrary] = []

    for library in libraries:
        distance_from_point: float = distance_between_points(library.point, point)

        distanced_libraries.append(DistancedLibrary(name=library.name, point=library.point, distance=distance_from_point))
    
    distanced_libraries.sort(key=lambda x: x.distance)

    # convert to libraries
    nearest_libraries: list[Library] = []

    for distanced_library in distanced_libraries[:n]:
        nearest_libraries.append(Library(name=distanced_library.name, point=distanced_library.point))
    
    return nearest_libraries
