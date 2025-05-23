###############################################
# Title: General Utility Functions
# Author: Christopher Romanillos
# Description: General-purpose utility methods
# Date: 3/06/25
# Version: 1.4
###############################################

import json
from pathlib import Path
from utils.logging import get_logger

# Use centralized logger
logger = get_logger("utils")

def save_to_file(data, file_path):
    """
    Save data to a JSON file.

    Args:
        data (dict): Data to be saved.
        file_path (str): Destination file path.
    """
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=2)
        logger.info("Data saved", file_path=file_path)
    except Exception as e:
        logger.error("Failed to save data", file_path=file_path, error=str(e))
        raise


def validate_data(data, required_fields):
    """
    Validate the structure and content of the API response data.

    Args:
        data (dict): The API response data.
        required_fields (list): List of required top-level keys.

    Returns:
        bool: True if data is valid, False otherwise.
    """
    for field in required_fields:
        if field not in data:
            logger.error("Missing field", field=field)
            return False
        if not isinstance(data[field], dict):
            logger.error("Field is not a dictionary", field=field)
            return False
        if not data[field]:
            logger.error("Field is empty", field=field)
            return False
    logger.info("Data validated successfully")
    return True


def check_api_errors(data):
    """
    Check for API-specific error messages in the response.

    Args:
        data (dict): The API response data.

    Returns:
        bool: True if no errors are found, False otherwise.
    """
    if "Note" in data:
        logger.error("API rate limit exceeded")
        return False
    if "Error Message" in data:
        logger.error("API error", error_message=data["Error Message"])
        return False
    logger.info("No API errors found")
    return True
