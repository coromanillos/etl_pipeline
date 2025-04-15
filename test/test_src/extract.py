##############################################
# Title: Alpha Vantage Time Series Intraday Extract
# Author: Christopher Romanillos
# Description: Extract data from Alpha Vantage
#   REST API, timestamp, save the file
# Date: 10/27/24
# Version: 1.3 (Refactored for structlog)
##############################################

from utils.logging import get_logger
from utils.utils import (
    save_to_file,
    validate_data,
    check_api_errors
)
from utils.config import load_config, load_env_variables
from utils.api_requests import fetch_api_data
from datetime import datetime
from pathlib import Path

# Initialize logger specific to this module
logger = get_logger(module_name="extract", log_file_path="logs/extract.log")

# Load configuration
config_path = Path(__file__).resolve().parent.parent / 'config' / 'config.yaml'
config = load_config(str(config_path))


def extract_data():
    """
    Extracts data from the Alpha Vantage API, validates it, and saves it to a file.
    Returns the extracted data.
    """
    try:
        logger.info("Starting data extraction...")

        # Retrieve API type for validation
        api_type = 'alpha_vantage_intraday'

        # Load validation rules
        validation_rules = config.get('validation', {}).get(api_type, {})
        required_keys = validation_rules.get('required_keys', [])

        # Validate required configuration keys
        missing_keys = [key for key in required_keys if key not in config['api']]
        if missing_keys:
            logger.error("Missing required config keys", missing_keys=missing_keys)
            return None

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

        if not data:
            logger.warning("No data received from API. Possible network issue.")
            return None

        # Check for API errors
        if not check_api_errors(data):
            logger.error("API returned an error. See logs for details.")
            return None

        # Validate data structure
        required_fields = ['Meta Data', 'Time Series (5min)']
        if not validate_data(data, required_fields):
            logger.error("Data validation failed. Required fields not found or invalid.")
            return None

        # Add extraction timestamp
        data['extraction_time'] = timestamp

        # Determine file save path
        raw_data_dir = Path(config['directories']['raw_data']).resolve()
        raw_data_dir.mkdir(parents=True, exist_ok=True)
        output_file_path = raw_data_dir / f"data_{timestamp}.json"

        # Save the data
        save_to_file(data, output_file_path)

        logger.info("Data extracted and saved successfully", path=str(output_file_path))

        return data

    except Exception:
        logger.exception("An unexpected error occurred during extraction.")
        return None


if __name__ == "__main__":
    extract_data()
