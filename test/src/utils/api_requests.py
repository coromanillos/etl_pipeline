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

def fetch_api_data(url, timeout):
    try:
        logger.info("Sending request", url=url, timeout=timeout)
        response = requests.get(url, timeout=timeout)
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
