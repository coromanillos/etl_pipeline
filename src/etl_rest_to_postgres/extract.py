#####################################################################################
# Title: Alpha Vantage Time Series Intraday Extract
# Author: Christopher Romanillos
# Description: Extract data from Alpha Vantage REST API, timestamp, and save the file
# Date: 2024-10-27 | Version: 1.9 (refactored for resilience and Airflow XCom compatibility)
#####################################################################################

from utils.api_requests import fetch_data
import logging

logger = logging.getLogger(__name__)

def extract_data(config):
    """
    Extract data from Alpha Vantage API and return as dict (no file saved).

    Args:
        config (dict): Config dictionary.

    Returns:
        dict or None: Extracted data dictionary or None on failure.
    """
    try:
        logger.info("Starting data extraction from Alpha Vantage API...")
        data = fetch_data(config["api"])

        if not data:
            logger.error("No data returned by the Alpha Vantage API.")
            return None

        logger.info("Data extraction successful.")
        return data

    except Exception as e:
        logger.exception(f"Exception during data extraction: {e}")
        return None
