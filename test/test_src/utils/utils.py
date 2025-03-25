##############################################
# Title: Modular Utilities Script
# Author: Christopher Romanillos
# Description: modular utils script
# Date: 3/06/25
# Version: 1.0
##############################################
import json
import logging
import sys
import yaml
import structlog


'''
def setup_logging(log_file):
    """Set up logging to both a file and stdout/stderr for Docker compatibility."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),  # Log to file
            logging.StreamHandler(sys.stdout),  # INFO logs to stdout
            logging.StreamHandler(sys.stderr),  # ERROR logs to stderr
        ]
    )
'''
def load_config(config_path):
    """Load configuration from a YAML file."""
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

# Load logging settings from config
config = load_config("config/config.yaml")
LOG_LEVEL = config.get("logging", {}).get("level", "INFO").upper()

def save_to_file(data, file_path):
    """Save data to a JSON file."""
    with open(file_path, 'w') as file:
        json.dump(data, file)
    logging.info(f"Data saved to {file_path}")

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
            logging.error(f"Missing field: {field}")
            return False
        if not isinstance(data[field], dict):
            logging.error(f"Field {field} is not a dictionary.")
            return False
        if not data[field]:  # Ensure the field is not empty
            logging.error(f"Field {field} is empty.")
            return False
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
        logging.error("API rate limit exceeded.")
        return False
    if "Error Message" in data:
        logging.error(f"API error: {data['Error Message']}")
        return False
    return True