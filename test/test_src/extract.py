##############################################
# Title: Alpha Vantage Time Series Intraday Extract
# Author: Christopher Romanillos
# Description: Extract data from Alpha Vantage
#   REST API, timestamp, save the file
# Date: 10/27/24
# Version: 1.1
##############################################

from utils.utils import (
    setup_logging, 
    save_to_file, 
    validate_data, 
    check_api_errors
)
from utils.config import load_config, load_env_variables
from utils.api_requests import fetch_api_data
from datetime import datetime
from pathlib import Path
import logging
import sys

# Define log directory and file path
log_dir = Path(__file__).resolve().parent.parent / 'logs'
log_dir.mkdir(parents=True, exist_ok=True)  # Ensure log directory exists
log_file_path = log_dir / 'extraction_record.log'

# Setup logging using the utility function for modular logging configuration
setup_logging(log_file_path)

def extract_data():
    """
    Extracts data from the Alpha Vantage API, validates it, and saves it to a file.
    Returns the extracted data.
    """
    try:
        logging.info("Starting data extraction...")

        # Load configuration (ensure path is resolved correctly)
        config_path = Path(__file__).resolve().parent.parent / 'config' / 'config.yaml'
        config = load_config(str(config_path))

        # Retrieve API type for validation
        api_type = 'alpha_vantage_intraday'

        # Load validation rules
        validation_rules = config.get('validation', {}).get(api_type, {})
        required_keys = validation_rules.get('required_keys', [])

        # Validate required configuration keys
        missing_keys = [key for key in required_keys if key not in config['api']]
        if missing_keys:
            raise ValueError(f"Missing required config keys: {', '.join(missing_keys)}")

        # Load environment variables
        api_key = load_env_variables('API_KEY')

        # Build API URL
        api_endpoint = config['api']['endpoint']
        timeout_value = config['api']['timeout']
        symbol = config['api']['symbol']
        interval = config['api'].get('interval', '5min')

        url = f"{api_endpoint}?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval={interval}&adjusted=false&apikey={api_key}"

        # Create a timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Fetch data
        data = fetch_api_data(url, timeout_value)
        
        # Check for empty response before proceeding
        if not data:
            raise ValueError("No data received from API. Possible network issue.")

        # Check for API errors
        if not check_api_errors(data):
            raise ValueError("API returned an error. See logs for details.")

        # Validate data structure
        required_fields = ['Meta Data', 'Time Series (5min)']
        if not validate_data(data, required_fields):
            raise ValueError("Data validation failed. Required fields not found or invalid.")

        # Add extraction timestamp
        data['extraction_time'] = timestamp

        # Determine file save path
        raw_data_dir = Path(__file__).resolve().parent.parent / 'data' / 'raw_data'
        raw_data_dir.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
        output_file_path = raw_data_dir / f"data_{timestamp}.json"

        # Save the data
        save_to_file(data, output_file_path)

        logging.info(f"Data extracted and saved successfully to path {output_file_path}")

        return data  # Return the extracted data so `main.py` can use it

    except ValueError as ve:
        logging.error(f"Validation error: {ve}", exc_info=True)
    except KeyError as ke:
        logging.error(f"KeyError: Missing key in the configuration or response. {ke}", exc_info=True)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)

    return None  # Return None if extraction fails (prevents errors in `main.py`)

# Ensure script only runs when executed directly (not on import)
if __name__ == "__main__":
    extract_data()
