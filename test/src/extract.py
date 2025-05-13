#####################################################################################
# # Title: Alpha Vantage Time Series Intraday Extract
# Author: Christopher Romanillos
# Description: Extract data from Alpha Vantage REST API, timestamp, and save the file
# Date: 10/27/24 | Version: 1.5 
#####################################################################################

from utils.logging import get_logger
from utils.utils import load_config
from utils.file_handler import save_raw_data
from utils.api_requests import fetch_data

def initialize_pipeline(config_path="../config/config.yaml"):
    config = load_config(config_path)
    log_file = config.get("extract", {}).get("log_file")
    if not log_file:
        raise ValueError("Missing configuration: extract.log_file")
    logger = get_logger("extract", log_file)
    logger.info("Extraction pipeline initialized.")
    return config, logger

def extract_data(config, logger):
    try:
        data = fetch_data(config["api"])
        if not data:
            logger.error("No data extracted from API.")
            return None

        raw_data_file = save_raw_data(data, config["directories"]["raw_data"])
        if not raw_data_file:
            logger.error("Failed to save extracted data.")
            return None

        logger.info("Extraction completed successfully.")
        return raw_data_file
    except Exception as e:
        logger.error("Extraction pipeline failed.", error=str(e))
        return None

if __name__ == "__main__":
    config, logger = initialize_pipeline()
    extract_data(config, logger)
