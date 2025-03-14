##############################################
# Title: Modular API Request Script
# Author: Christopher Romanillos
# Description: modular api_request script
# Date: 11/23/24
# Version: 1.0
##############################################
import requests
import logging

def fetch_api_data(url, timeout):
    """Send a GET request to the API and return the data."""
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        logging.error(f"Request timed out after {timeout} seconds.")
        raise
    except requests.exceptions.ConnectionError:
        logging.error("A connection error occurred.")
        raise
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
        raise
    except requests.exceptions.RequestException as err:
        logging.error(f"An unexpected error occurred: {err}")
        raise