"""
Finds the nearest library to a given postcode
"""

# Python import entire module
import datetime
import re
import requests
import sqlite3

# Python import specific items from a module
from dataclasses import dataclass
from math import sin, cos, acos, radians
from typing import Union

# Custom import
import constants

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

def create_database(conn: sqlite3.Connection) -> None:
    """
    Creates the database if it doesn't exist, and creates the libraries table if it doesn't exist

    Parameters:
        conn (sqlite3.Connection): the connection to the database
    Returns:
        None
    """

    query: str = get_query_from_file("createLibraryTable.sql")

    conn.execute(query)

    conn.commit()

def get_oldest_date(conn: sqlite3.Connection) -> datetime.date:
    """
    Gets the oldest date in the database

    Parameters:
        conn (sqlite3.Connection): the connection to the database
    Returns:
        datetime.date - the oldest date in the database. If there are no dates, returns 1/1/1
    """
    
    cursor: sqlite3.Cursor = conn.cursor()

    query: str = get_query_from_file("getOldestDate.sql")

    cursor.execute(query)
    oldest_date = cursor.fetchone()[0]

    if oldest_date:
        return datetime.datetime.strptime(oldest_date, "%Y-%m-%d").date()
    else:
        return datetime.date(1, 1, 1)

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

def clear_records(conn: sqlite3.Connection) -> None:
    """
    Clears the records in the database

    Parameters:
        conn (sqlite3.Connection): the connection to the database
    Returns:
        None
    """

    cursor: sqlite3.Cursor = conn.cursor()

    query: str = get_query_from_file("clearLibraries.sql")

    cursor.execute(query)

    conn.commit()

def execute_library_sparql_query() -> list[Library]:
    """
    Executes the library sparql query

    Parameters:
        None
    Returns:
        list[Library] - the libraries from wikidata
    """
    
    headers = {
        "Accept": "application/sparql-results+json"
    }
    sparql_query: str = get_query_from_file("getLibraries.sparql")

    response: requests.Response = requests.get(constants.SPARQL_WIKIDATA_URL, headers=headers, params={"query": sparql_query})

    libraries: list[Library] = []

    try:
        for result in response.json()["results"]["bindings"]:
            name: str = result["itemLabel"]["value"]

            add: bool = True

            if "endTime" in result or "startTime" in result:
                # print the end time value
                print(name)
                add = False

            if "coord" in result:
                latitude, longitude = map(
                    float, result["coord"]["value"].split("(")[1].split(")")[0].split())
            else:
                latitude = -999
                longitude = -999
            
            # Swap latitude and longitude
            latitude, longitude = longitude, latitude

            if latitude in constants.KNOWN_BAD_LATITUDES:
                add = False

            point: Point = Point(latitude=latitude, longitude=longitude)
            library: Library = Library(name=name, point=point)

            if add:
                libraries.append(library)
    except:
        print("Error")
        with open("error.txt", "w") as f:
            f.write(response.text)
        print(response.status_code)
        exit()
    
    return libraries

def add_libraries_to_database(conn: sqlite3.Connection, libraries: list[Library]) -> None:
    """
    Adds the libraries to the database

    Parameters:
        conn (sqlite3.Connection): the connection to the database
        libraries (list[Library]): the libraries to add to the database
    Returns:
        None
    """

    cursor: sqlite3.Cursor = conn.cursor()

    query: str = get_query_from_file("addLibrary.sql")

    for library in libraries:
        cursor.execute(query, (library.name, library.point.latitude, library.point.longitude))

    conn.commit()

def get_postcode_from_user() -> str:
    """
    Gets a postcode from the user

    Parameters:
        None
    Returns:
        str - the postcode
    """

    postcode: str = ""

    # ensure postcode matches regex

    while not re.match(constants.POSTCODE_REGEX, postcode):
        postcode = input("Please enter a postcode: ").upper()

    return postcode

def check_postcode_valid(postcode: str) -> bool:
    """
    Checks if a postcode is valid

    Parameters:
        postcode (str): the postcode to check
    Returns:
        bool - True if the postcode is valid, False otherwise
    """

    r: requests.Response = requests.get(f"https://api.postcodes.io/postcodes/{postcode}/validate")

    if r.status_code != 200:
        return False
    
    return r.json()["result"]

def get_latitude_and_longitude_from_postcode(postcode: str) -> Point:
    """
    Gets the latitude and longitude from a postcode

    Parameters:
        postcode (str): the postcode to get the latitude and longitude from
    Returns:
        Point - the latitude and longitude of the postcode
    """

    r: requests.Response = requests.get(f"https://api.postcodes.io/postcodes/{postcode}")

    if r.status_code != 200:
        raise Exception("Error")

    data = r.json()["result"]

    latitude = float(data["latitude"])
    longitude = float(data["longitude"])

    return Point(latitude=latitude, longitude=longitude)

def get_libraries_from_database(conn: sqlite3.Connection) -> list[Library]:
    """
    Gets the libraries from the database

    Parameters:
        conn (sqlite3.Connection): the connection to the database
    Returns:
        list[Library] - the libraries from the database
    """

    cursor: sqlite3.Cursor = conn.cursor()

    query: str = get_query_from_file("getLibraries.sql")

    cursor.execute(query)

    libraries: list[Library] = []

    for row in cursor.fetchall():
        library: Library = Library(name=row[0], point=Point(latitude=row[1], longitude=row[2]))
        libraries.append(library)

    return libraries

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

def find_nearest_library(libraries: list[Library], point: Point) -> Union[Library, None]:
    """
    Finds the nearest library to a point

    Parameters:
        libraries (list[Library]): the libraries to search
        point (Point): the point to find the nearest library to
    Returns:
        Union[Library, None] - the nearest library to the point, or None if there are no libraries
    """

    nearest_library: list[Library] = find_nearest_n_libraries(libraries, point, 1)

    if len(nearest_library) == 0:
        return None
    return nearest_library[0]

def is_integer(value: str) -> bool:
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

def get_integer_from_user(prompt: str) -> int:
    """
    Gets an integer from the user

    Parameters:
        prompt (str): the prompt to display
    Returns:
        int - the integer entered by the user
    """
    
    value: str = ""

    while not is_integer(value):
        value = input(prompt).strip()

        if not is_integer(value):
            print("Invalid input")
    
    return int(value)

def main() -> None:
    """
    The main function

    Parameters:
        None
    Returns:
        None
    """

    with sqlite3.connect("library.db") as conn:
        create_database(conn)
        
        oldest_date: datetime.date = get_oldest_date(conn)

        if check_date_older_than_days(oldest_date, constants.DAYS_TO_REFRESH_DB):
            clear_records(conn)
        
            libraries: list[Library] = execute_library_sparql_query()

            add_libraries_to_database(conn, libraries)
        
        postcode: str = get_postcode_from_user()

        if not check_postcode_valid(postcode):
            print("Invalid postcode")
            return

        point: Point = get_latitude_and_longitude_from_postcode(postcode)

        libraries: list[Library] = get_libraries_from_database(conn)  

    nearest_library: Union[Library, None] = find_nearest_library(libraries, point)

    if not nearest_library:
        print("No libraries found")
        return

    print(f"The nearest library is {nearest_library.name}")  
    
    how_many_libraries: int = get_integer_from_user("How many libraries do you want to find? ")

    nearest_libraries: list[Library] = find_nearest_n_libraries(libraries, point, how_many_libraries)

    print(f"The nearest {how_many_libraries} libraries are:")

    for library in nearest_libraries:
        print(library.name)

if __name__ == "__main__":
    main()
