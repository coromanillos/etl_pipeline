##############################################
# Title: API Requests Utility
# Author: Christopher Romanillos
# Description: Handles API requests with structured logging
# Date: 04/02/25
# Version: 1.3
##############################################

import requests
import logging

logger = logging.getLogger(__name__)

def fetch_data(api_config):
    url = api_config["endpoint"]
    timeout = api_config["timeout"]
    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": api_config["symbol"],
        "interval": api_config["interval"],
        "apikey": api_config["key"],
    }

    try:
        logger.info(f"Sending request to API: {url}")
        response = requests.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        logger.info(f"Request successful: {response.status_code}")
        return response.json()

    except requests.exceptions.Timeout:
        logger.error("Request timed out", exc_info=True)
        raise

    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error: {e}", exc_info=True)
        raise

    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error: {http_err}", exc_info=True)
        raise

    except requests.exceptions.RequestException as err:
        logger.error(f"Unexpected request error: {err}", exc_info=True)
        raise
