##############################################
# Title: API Requests Utility
# Author: Christopher Romanillos
# Description: Handles API requests with structured logging
# Date: 04/02/25
# Version: 1.3
##############################################

import requests
from utils.logging import get_logger

# Get logger with default base-case logging (utilities.log)
logger = get_logger(__file__)

def fetch_data(api_config):
    """
    Fetch data from the API using the provided configuration.

    Args:
        api_config (dict): API configuration containing endpoint, key, timeout, etc.

    Returns:
        dict: Parsed JSON response from the API.

    Raises:
        Exception: If the request fails or is unsuccessful.
    """
    url = api_config["endpoint"]
    timeout = api_config["timeout"]
    params = {
        "function": "TIME_SERIES_INTRADAY",  # Assuming 'intraday' for this case
        "symbol": api_config["symbol"],
        "interval": api_config["interval"],
        "apikey": api_config["key"]
    }

    try:
        logger.info("Sending request to API", url=url, timeout=timeout, params=params)
        response = requests.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        logger.info("Request successful", status_code=response.status_code)
        return response.json()

    except requests.exceptions.Timeout:
        logger.error("Request timed out", timeout=timeout)
        raise

    except requests.exceptions.ConnectionError as e:
        logger.error("Connection error occurred", error=str(e))
        raise

    except requests.exceptions.HTTPError as http_err:
        logger.error("HTTP error occurred", status_code=response.status_code, error=str(http_err))
        raise

    except requests.exceptions.RequestException as err:
        logger.error("Unexpected request exception", error=str(err))
        raise
