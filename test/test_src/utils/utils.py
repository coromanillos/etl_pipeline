##############################################
# Title: General Utility Functions
# Author: Christopher Romanillos
# Description: General-purpose utility methods
# Date: 3/06/25
# Version: 1.2
###############################################

import json
import yaml
import os
from logging import setup_logging  # Ensure you import your setup_logging

# Initialize the logger
logger = setup_logging()

def load_config():
    """
    Load the YAML configuration file.

    Returns:
        dict: Parsed configuration.

    Raises:
        RuntimeError: If the config file is not found or invalid.
    """
    config_path = "config/config.yaml"
    if not os.path.exists(config_path):
        logger.error(f"Config file not found: {config_path}")
        raise RuntimeError(f"Config file not found: {config_path}")
    
    with open(config_path, "r") as file:
        try:
            return yaml.safe_load(file)
        except yaml.YAMLError as e:
            logger.error("Error parsing config.yaml", error=str(e))
            raise RuntimeError("Error parsing config.yaml") from e

def save_to_file(data, file_path, logger=logger):
    """
    Save data to a JSON file.

    Args:
        data (dict): Data to be saved.
        file_path (str): Destination file path.
        logger (structlog.BoundLogger, optional): Logger instance.
    """
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=2)
        logger.info("Data saved", file_path=file_path)
    except Exception as e:
        logger.error("Failed to save data", file_path=file_path, error=str(e))
        raise

def validate_data(data, required_fields, logger=logger):
    """
    Validate the structure and content of the API response data.

    Args:
        data (dict): The API response data.
        required_fields (list): List of required top-level keys.
        logger (structlog.BoundLogger): Logger instance.

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
    return True

def check_api_errors(data, logger=logger):
    """
    Check for API-specific error messages in the response.

    Args:
        data (dict): The API response data.
        logger (structlog.BoundLogger): Logger instance.

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
