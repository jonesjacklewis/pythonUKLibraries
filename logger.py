# Standard Library Imports
import datetime
import os

# Custom Imports
import constants

def create_log_file() -> None:
    """
    Creates the log file if it doesn't exist

    Parameters:
        None
    Returns:
        None
    """

    if not os.path.exists(constants.LOG_FILE):
        with open(constants.LOG_FILE, "w") as f:
            f.write("")

def log(calling_file: str, message: str) -> None:
    """
    Logs a message to the log file

    Parameters:
        message (str): the message to log
    Returns:
        None
    """

    create_log_file()

    # A log should include the timestamp, the calling file, and the message
    log_message: str = f"{datetime.datetime.now()}: {calling_file}: {message}"

    with open(constants.LOG_FILE, "a") as f:
        f.write(log_message + "\n")