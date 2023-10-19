# Third Party Imports
import requests

# Custom Imports
import constants
import database_handling

# Custom From Imports
from models import Library, Point


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
    sparql_query: str = database_handling.get_query_from_file("getLibraries.sparql")

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