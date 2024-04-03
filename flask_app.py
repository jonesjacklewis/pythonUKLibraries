# Standard Library Imports
import datetime
import sqlite3

# Third Party From Imports
from flask import Flask
from flask_cors import CORS, cross_origin


# Custom Imports
import constants
import database_handling
import logger
import third_party_integrations
import utilities

# Custom From Imports
from models import Point, Library

# Create Flask app
app = Flask(__name__)
cors = CORS(app)

app.config['CORS_HEADERS'] = 'Content-Type'

# crreate endpoint / for hello world
@app.route('/')
@cross_origin()
def hello_world():
    return 'Hello, World!'

# Create endpoint for getting libraries
@app.route('/postcode/<string:postcode>/count/<int:count>', methods=['GET'])
@cross_origin()
def get_libraries(postcode: str, count: int):
    """
    Endpoint for getting libraries from database
    :param postcode: postcode to search from
    :param count: number of libraries to return
    :return: dictionary containing libraries, count, postcode and success or error
    """

    logger.log(__file__, f"Getting libraries for postcode {postcode} and count {count}")

    with sqlite3.connect(constants.DATABASE_FILE) as conn:
        logger.log(__file__, "Connected to database")
        database_handling.create_database(conn)

        logger.log(__file__, "Checking if database needs to be refreshed")

        oldest_date: datetime.date = database_handling.get_oldest_date(conn)

        if utilities.check_date_older_than_days(oldest_date, constants.DAYS_TO_REFRESH_DB):
            logger.log(__file__, "Database needs to be refreshed")
            logger.log(__file__, "Clearing records from database")
            database_handling.clear_records(conn)
        
            logger.log(__file__, "Getting libraries from wikidata")

            try:
                libraries: list[Library] = third_party_integrations.execute_library_sparql_query()
            except Exception as e:
                logger.log(__file__, f"Error getting libraries from wikidata: {e}")
                return {
                    "success": False,
                    "error": "Error getting libraries from wikidata"
                }, 500

            logger.log(__file__, "Adding libraries to database")
            database_handling.add_libraries_to_database(conn, libraries)

        logger.log(__file__, "Getting latitude and longitude from postcode")
        if not third_party_integrations.check_postcode_valid(postcode):
            return {
                "success": False,
                "error": "Invalid postcode"
            }, 400
        
        point: Point = third_party_integrations.get_latitude_and_longitude_from_postcode(postcode)

        logger.log(__file__, "Getting libraries from database")
        libraries: list[Library] = database_handling.get_libraries_from_database(conn)

        nearest_libraries: list[Library] = utilities.find_nearest_n_libraries(libraries, point, count)

        return {
            "success": True,
            "postcode": postcode,
            "count": len(nearest_libraries),
            "libraries": [library.__dict__ for library in nearest_libraries]
        }

@app.route('/latitude/<string:latitude>/longitude/<string:longitude>/count/<int:count>', methods=['GET'])
@cross_origin()
def get_libraries_by_coordinates(latitude: str, longitude: str, count: int):
    """
    Endpoint for getting libraries from database by latitutde and longitutde
    :param latitude: latitude to search from
    :param longitude: longitude to search from
    :param count: number of libraries to return
    :return: dictionary containing libraries, count, latitude,  longitude, and success or error
    """

    logger.log(__file__, f"Getting libraries for latitude {latitude}, longitude {longitude} and count {count}")

    with sqlite3.connect(constants.DATABASE_FILE) as conn:
        logger.log(__file__, "Connected to database")
        database_handling.create_database(conn)

        logger.log(__file__, "Checking if database needs to be refreshed")

        oldest_date: datetime.date = database_handling.get_oldest_date(conn)

        if utilities.check_date_older_than_days(oldest_date, constants.DAYS_TO_REFRESH_DB):
            logger.log(__file__, "Database needs to be refreshed")
            logger.log(__file__, "Clearing records from database")
            database_handling.clear_records(conn)
        
            logger.log(__file__, "Getting libraries from wikidata")

            try:
                libraries: list[Library] = third_party_integrations.execute_library_sparql_query()
            except Exception as e:
                logger.log(__file__, f"Error getting libraries from wikidata: {e}")
                return {
                    "success": False,
                    "error": "Error getting libraries from wikidata"
                }, 500

            logger.log(__file__, "Adding libraries to database")
            database_handling.add_libraries_to_database(conn, libraries)

        logger.log(__file__, "Getting latitude and longitude from postcode")
        
        if not utilities.is_valid_latitude(latitude):
            return {
                "success": False,
                "error": f"Invalid latitude {latitude}"
            }, 400

        if not utilities.is_valid_longitude(longitude):
            return {
                "success": False,
                "error": f"Invalid longitude {longitude}"
            }, 400

        logger.log(__file__, "Getting libraries from database")
        libraries: list[Library] = database_handling.get_libraries_from_database(conn)

        point: Point = Point(float(latitude), float(longitude))

        nearest_libraries: list[Library] = utilities.find_nearest_n_libraries(libraries, point, count)

        return {
            "success": True,
            "latitude": point.latitude,
            "longitude": point.longitude,
            "count": len(nearest_libraries),
            "libraries": [library.__dict__ for library in nearest_libraries]
        }

if __name__ == '__main__':
    app.run(port = constants.FLASK_PORT)