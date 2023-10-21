# Standard Library Imports
import datetime
import os
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

    query_file: str = os.path.join("sql", "createLibraryTable.sql")
    query: str = utilities.get_query_from_file(query_file)

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

    query_file: str = os.path.join("sql", "getOldestDate.sql")
    query: str = utilities.get_query_from_file(query_file)

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

    query_file: str = os.path.join("sql", "clearLibraries.sql")
    query: str = utilities.get_query_from_file(query_file)

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

    query_file: str = os.path.join("sql", "addLibrary.sql")
    query: str = utilities.get_query_from_file(query_file)

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

    query_file: str = os.path.join("sql", "getLibraries.sql")
    query: str = utilities.get_query_from_file(query_file)

    cursor.execute(query)

    libraries: list[Library] = []

    for row in cursor.fetchall():
        library: Library = Library(name=row[0], point=Point(latitude=row[1], longitude=row[2]))
        libraries.append(library)

    return libraries