#####################################################################################
# Title: Alpha Vantage Time Series Intraday Extract
# Author: Christopher Romanillos
# Description: Extract data from Alpha Vantage REST API, timestamp, and save the file
# Date: 10/27/24 | Version: 1.8 (refactored for modern logging)
#####################################################################################

from utils.file_handler import save_raw_data
from utils.api_requests import fetch_data

def extract_data(config, logger):
    try:
        data = fetch_data(config["api"])
        if not data:
            logger.error("No data extracted from API.")
            return None

        raw_data_file = save_raw_data(data, config["directories"]["raw_data"])
        if not raw_data_file:
            logger.error("Failed to save extracted data to raw_data directory.")
            return None

        logger.info(f"Extraction completed successfully. Raw data saved to: {raw_data_file}")
        return raw_data_file
    except Exception as e:
        logger.exception("Extraction pipeline failed with an exception.")
        return None