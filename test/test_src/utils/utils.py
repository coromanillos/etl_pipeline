##############################################
# Title: General Utility Functions
# Author: Christopher Romanillos
# Description: General-purpose utility methods
# Date: 3/06/25
# Version: 1.1
###############################################

import json
import yaml

def load_config():
    """Load YAML configuration."""
    with open("config/config.yaml", "r") as file:
        return yaml.safe_load(file)

def save_to_file(data, file_path, logger):
    """Save data to a JSON file."""
    with open(file_path, 'w') as file:
        json.dump(data, file)
    logger.info("Data saved", file_path=file_path)

def validate_data(data, required_fields, logger):
    """
    Validate the structure and content of the API response data.

    Args:
        data (dict): The API response data.
        required_fields (list): List of required top-level keys.
        logger (structlog.BoundLogger): The logger instance to log messages.

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
        if not data[field]:  # Ensure the field is not empty
            logger.error("Field is empty", field=field)
            return False
    return True

def check_api_errors(data, logger):
    """
    Check for API-specific error messages in the response.

    Args:
        data (dict): The API response data.
        logger (structlog.BoundLogger): The logger instance to log messages.

    Returns:
        bool: True if no errors are found, False otherwise.
    """
    if "Note" in data:
        logger.error("API rate limit exceeded")
        return False
    if "Error Message" in data:
        logger.error("API error", error_message=data["Error Message"])
        return False
    return True
