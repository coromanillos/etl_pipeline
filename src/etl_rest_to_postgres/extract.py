##############################################
# Title: Alpha Vantage Time Series Intraday Extract
# Author: Christopher Romanillos
# Description: Extracts data from Alpha Vantage REST API
# Date: 2024-10-27 | Version: 2.0 (centralized config)
##############################################

import logging
from src.utils.api_requests import fetch_data

logger = logging.getLogger(__name__)

def extract_data(config):
    try:
        logger.info("🔍 Extracting from Alpha Vantage API...")
        data = fetch_data(config["api"])
        if not data:
            logger.error("No data returned by API.")
            return None
        logger.info("✅ API extraction successful.")
        return data
    except Exception as e:
        logger.exception(f"❌ Exception during data extraction: {e}")
        return None