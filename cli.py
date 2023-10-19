"""
Finds the nearest library to a given postcode
"""

# Standard Library Imports
import datetime
import re
import sqlite3

# Standard From Imports
from typing import Union

# Custom Import
import constants
import database_handling
import third_party_integrations
import utilities

# Custom From Imports
from models import Library, Point

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

def get_integer_from_user(prompt: str) -> int:
    """
    Gets an integer from the user

    Parameters:
        prompt (str): the prompt to display
    Returns:
        int - the integer entered by the user
    """
    
    value: str = ""

    while not utilities.is_valid_integer(value):
        value = input(prompt).strip()

        if not utilities.is_valid_integer(value):
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
        database_handling.create_database(conn)
        
        oldest_date: datetime.date = database_handling.get_oldest_date(conn)

        if utilities.check_date_older_than_days(oldest_date, constants.DAYS_TO_REFRESH_DB):
            database_handling.clear_records(conn)
        
            libraries: list[Library] = third_party_integrations.execute_library_sparql_query()

            database_handling.add_libraries_to_database(conn, libraries)
        
        postcode: str = get_postcode_from_user()

        if not third_party_integrations.check_postcode_valid(postcode):
            print("Invalid postcode")
            return

        point: Point = third_party_integrations.get_latitude_and_longitude_from_postcode(postcode)

        libraries: list[Library] = database_handling.get_libraries_from_database(conn)  

    nearest_library_list: Union[list[Library], None] = utilities.find_nearest_n_libraries(libraries, point, 1)

    if not nearest_library_list:
        print("No libraries found")
        return
    
    nearest_library: Library = nearest_library_list[0]

    if not nearest_library:
        print("No libraries found")
        return

    print(f"The nearest library is {nearest_library.name}")  
    
    how_many_libraries: int = get_integer_from_user("How many libraries do you want to find? ")

    nearest_libraries: list[Library] = utilities.find_nearest_n_libraries(libraries, point, how_many_libraries)

    print(f"The nearest {how_many_libraries} libraries are:")

    for library in nearest_libraries:
        print(library.name)

if __name__ == "__main__":
    main()
