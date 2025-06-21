#####################################################################################
# Title: Alpha Vantage Time Series Intraday Extract
# Author: Christopher Romanillos
# Description: Extract data from Alpha Vantage REST API, timestamp, and save the file
# Date: 2024-10-27 | Version: 1.9 (refactored for resilience and Airflow XCom compatibility)
#####################################################################################

from utils.file_handler import save_raw_data
from utils.api_requests import fetch_data

def extract_data(config, logger):
    """
    Extracts intraday time series data from the Alpha Vantage API and saves it to disk.

    Args:
        config (dict): Loaded config.yaml dictionary.
        logger (Logger): Initialized structured logger.

    Returns:
        str or None: Path to the raw data file if successful, else None.
    """
    try:
        logger.info("Starting data extraction from Alpha Vantage API...")
        data = fetch_data(config["api"])
        
        if not data:
            logger.error("No data returned by the Alpha Vantage API.")
            return None

        raw_data_path = save_raw_data(data, config["directories"]["raw_data"])
        if not raw_data_path:
            logger.error("Failed to save raw data to disk.")
            return None

        logger.info(f"Raw data successfully saved to: {raw_data_path}")
        return raw_data_path

    except Exception as e:
        logger.exception(f"Exception during data extraction: {e}")
        return None
