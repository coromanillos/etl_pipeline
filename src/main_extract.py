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

# Set logging configuration to directory logs/extraction_record.log
log_file_path = Path(__file__).resolve().parent.parent / 'logs' / 'extraction_record.log'
setup_logging(log_file_path)

try:
    # Load configuration from config.yaml to a variable
    config = load_config('../config/config.yaml')

    # Retrieve API type for validation (i.e. "alpha_vantage_intraday")
    api_type = 'alpha_vantage_intraday' # Validation type via config.yaml

    # Load validation rules for the specific API type
    validation_rules = config.get('validation', {}).get(api_type, {})
    required_keys = validation_rules.get('required_keys', [])

    # Validate required configuration keys are present
    missing_keys = [key for key in required_keys if key not in config['api']]
    if missing_keys:
        raise ValueError(f"Missing required config keys: {', '.join(missing_keys)}")

    # Load environment variables
    api_key = load_env_variables('API_KEY')

    # Build API URL with variables
    api_endpoint = config['api']['endpoint']
    timeout_value = config['api']['timeout']
    symbol = config['api']['symbol']
    interval = config['api'].get('interval', '5min')

    # Finished API URL
    url = f"{api_endpoint}?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval={interval}&adjusted=false&apikey={api_key}"

    # Create a timestamp variable for filenames and data tracking
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Fetch data from API
    data = fetch_api_data(url, timeout_value)
    
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
    output_file_path = raw_data_dir / f"data_{timestamp}.json"

    # Save the data
    save_to_file(data, output_file_path)

    logging.info(f"All tests passed. Data extracted and saved successfully to path {output_file_path}")

except ValueError as ve:
    logging.error(f"Validation error: {ve}")
except KeyError as ke:
    logging.error(f"KeyError: Missing key in the configuration or response. {ke}")
except Exception as e:
    logging.error(f"An unexpected error occurred: {e}")