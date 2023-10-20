# Standard Library Imports
import datetime
import sqlite3

# Third Party From Imports
from flask import Flask

# Custom Imports
import constants
import database_handling
import third_party_integrations
import utilities

# Custom From Imports
from models import Point, Library

# Create Flask app
app = Flask(__name__)

# Create endpoint for getting libraries
@app.route('/postcode/<string:postcode>/count/<int:count>', methods=['GET'])
def get_libraries(postcode: str, count: int):
    """
    Endpoint for getting libraries from database
    :param postcode: postcode to search from
    :param count: number of libraries to return
    :return: dictionary containing libraries, count, postcode and success or error
    """

    with sqlite3.connect("library.db") as conn:
        database_handling.create_database(conn)

        oldest_date: datetime.date = database_handling.get_oldest_date(conn)

        if utilities.check_date_older_than_days(oldest_date, constants.DAYS_TO_REFRESH_DB):
            database_handling.clear_records(conn)
        
            libraries: list[Library] = third_party_integrations.execute_library_sparql_query()

            database_handling.add_libraries_to_database(conn, libraries)

        if not third_party_integrations.check_postcode_valid(postcode):
            return {
                "success": False,
                "error": "Invalid postcode"
            }, 400
        
        point: Point = third_party_integrations.get_latitude_and_longitude_from_postcode(postcode)

        libraries: list[Library] = database_handling.get_libraries_from_database(conn)

        nearest_libraries: list[Library] = utilities.find_nearest_n_libraries(libraries, point, count)

        return {
            "success": True,
            "postcode": postcode,
            "count": len(nearest_libraries),
            "libraries": [library.__dict__ for library in nearest_libraries]
        }

if __name__ == '__main__':
    app.run(port = 8080)