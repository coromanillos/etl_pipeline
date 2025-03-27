##############################################
# Title: Modular Utilities Script
# Author: Christopher Romanillos
# Description: Modular utils script
# Date: 3/06/25
# Version: 1.0
############################################### 
import json
import logging
import yaml
import structlog
import os
from logging.config import dictConfig

# Load config
def load_config():
    with open("config/config.yaml", "r") as file:
        return yaml.safe_load(file)
    
# Setup logging to a single file
def setup_logging():
    config = load_config()
    log_file = config["logging"]["log_file"]

    # Ensure log directory exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Logging configuration for a single log file
    dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": structlog.processors.JSONRenderer()
            }
        },
        "handlers": {
            "info_stdout": {
                "class": "logging.StreamHandler",
                "formatter": "json",
                "stream": "ext://sys.stdout",
                "level": "INFO"
            },
            "error_stderr": {
                "class": "logging.StreamHandler",
                "formatter": "json",
                "stream": "ext://sys.stderr",
                "level": "ERROR"
            },
            "file": {
                "class": "logging.FileHandler",
                "filename": log_file,
                "formatter": "json",
                "level": "INFO"
            }
        },
        "root": {
            "level": "INFO",
            "handlers": ["info_stdout", "error_stderr", "file"]
        }
    })

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        cache_logger_on_first_use=True
    )

    return structlog.get_logger()

# Get logger instance
logger = setup_logging()

def save_to_file(data, file_path):
    """Save data to a JSON file."""
    with open(file_path, 'w') as file:
        json.dump(data, file)
    logger.info("Data saved", file_path=file_path)

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
        if not data[field]:  # Ensure the field is not empty
            logger.error("Field is empty", field=field)
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
        logger.error("API rate limit exceeded")
        return False
    if "Error Message" in data:
        logger.error("API error", error_message=data["Error Message"])
        return False
    return True
