# Standard Library Imports
import datetime
import sqlite3

# Custom Imports
import utilities

# Custom From Imports
from models import Library, Point

def create_database(conn: sqlite3.Connection) -> None:
    """
    Creates the database if it doesn't exist, and creates the libraries table if it doesn't exist

    Parameters:
        conn (sqlite3.Connection): the connection to the database
    Returns:
        None
    """

    query: str = utilities.get_query_from_file("createLibraryTable.sql")

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

    query: str = utilities.get_query_from_file("getOldestDate.sql")

    cursor.execute(query)
    oldest_date = cursor.fetchone()[0]

    if oldest_date:
        return datetime.datetime.strptime(oldest_date, "%Y-%m-%d").date()
    else:
        return datetime.date(1, 1, 1)

def clear_records(conn: sqlite3.Connection) -> None:
    """
    Clears the records in the database

    Parameters:
        conn (sqlite3.Connection): the connection to the database
    Returns:
        None
    """

    cursor: sqlite3.Cursor = conn.cursor()

    query: str = utilities.get_query_from_file("clearLibraries.sql")

    cursor.execute(query)

    conn.commit()

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

    query: str = utilities.get_query_from_file("addLibrary.sql")

    for library in libraries:
        cursor.execute(query, (library.name, library.point.latitude, library.point.longitude))

    conn.commit()

def get_libraries_from_database(conn: sqlite3.Connection) -> list[Library]:
    """
    Gets the libraries from the database

    Parameters:
        conn (sqlite3.Connection): the connection to the database
    Returns:
        list[Library] - the libraries from the database
    """

    cursor: sqlite3.Cursor = conn.cursor()

    query: str = utilities.get_query_from_file("getLibraries.sql")

    cursor.execute(query)

    libraries: list[Library] = []

    for row in cursor.fetchall():
        library: Library = Library(name=row[0], point=Point(latitude=row[1], longitude=row[2]))
        libraries.append(library)

    return libraries