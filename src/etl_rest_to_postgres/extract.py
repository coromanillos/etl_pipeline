##############################################
# Title: Alpha Vantage Time Series Intraday Extract
# Author: Christopher Romanillos
# Description: Extracts data from Alpha Vantage REST API
# Date: 2024-10-27 | Version: 2.0 (centralized config)
##############################################

import logging
from src.utils.api_requests import fetch_data

logger = logging.getLogger(__name__)

def extract_data(config: dict, fetch_fn=None) -> dict | None:
    """
    Extracts raw data from Alpha Vantage API.
    
    Args:
        config (dict): Config with API details.
        fetch_fn (callable, optional): Override for API fetch function (for testing).
    
    Returns:
        dict or None: Raw JSON data if successful, else None.
    """
    fetch_fn = fetch_fn or fetch_data
    try:
        logger.info("🔍 Extracting from Alpha Vantage API...")
        data = fetch_fn(config["api"])
        if not data:
            logger.error("No data returned by API.")
            return None
        logger.info("✅ API extraction successful.")
        return data
    except Exception as e:
        logger.exception(f"❌ Exception during data extraction: {e}")
        return None
