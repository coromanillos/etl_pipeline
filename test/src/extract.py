##############################################
# Title: Alpha Vantage Time Series Intraday Extract
# Author: Christopher Romanillos
# Description: Extract data from Alpha Vantage
#   REST API, timestamp, save the file
# Date: 10/27/24
# Version: 1.3 (Refactored for structlog)
##############################################

import json
from utils.logging import get_logger
from utils.utils import load_config
from utils.file_handler import save_raw_data
from utils.api_requests import fetch_data

def initialize_pipeline(config_path="../config/config.yaml"):
    """
    Loads and validates configuration settings.
    Returns validated configuration and logger instance.
    """
    # Load configuration
    config = load_config(config_path)
    
    # Get log file path for extraction
    log_file = config.get("extract", {}).get("log_file")
    if not log_file:
        raise ValueError("Missing required configuration key: extract.log_file")

    # Initialize logger
    logger = get_logger(module_name="extract.py", log_file_path=log_file)
    
    # Validate required fields for extraction
    required_fields = config.get("extract", {}).get("required_fields")
    if not required_fields:
        raise ValueError("Missing required configuration key: extract.required_fields")

    logger.info("Pipeline initialized successfully")
    return config, logger

def extract_data(config, logger):
    """
    Main function to extract data from Alpha Vantage API.
    """
    try:
        # Call API and fetch data
        data = fetch_data(config["api"])

        # Validate fetched data
        if not data:
            logger.error("No data extracted from API")
            return None

        # Save raw data to the specified directory
        raw_data_file = save_raw_data(data, config["directories"]["raw_data"])
        if raw_data_file:
            logger.info(f"Data extracted and saved to {raw_data_file}")
        else:
            logger.error("Failed to save raw data")
            return None
        
        return raw_data_file

    except Exception as e:
        logger.error("Unexpected extraction failure", error=str(e))
        return None

if __name__ == "__main__":
    # Initialize pipeline and logger
    config, logger = initialize_pipeline(config_path="../config/config.yaml")
    
    # Extract data
    extract_data(config, logger)
