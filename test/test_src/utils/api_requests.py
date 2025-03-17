import requests
import logging
import sys

# Set up logging to both stdout and stderr for Docker logging best practices
logger = logging.getLogger()

# Create a handler for stdout (regular logs)
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.INFO)  # Adjust log level if necessary

# Create a handler for stderr (error logs)
stderr_handler = logging.StreamHandler(sys.stderr)
stderr_handler.setLevel(logging.ERROR)  # Only log ERROR and CRITICAL to stderr

# Define formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Apply the formatter to both handlers
stdout_handler.setFormatter(formatter)
stderr_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(stdout_handler)
logger.addHandler(stderr_handler)

# Set the default log level to INFO
logger.setLevel(logging.INFO)

def fetch_api_data(url, timeout):
    """Send a GET request to the API and return the data."""
    try:
        logger.info(f"Sending request to {url} with timeout {timeout} seconds")
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        logger.info("Request successful")
        return response.json()
    except requests.exceptions.Timeout:
        logger.error(f"Request timed out after {timeout} seconds.")
        raise
    except requests.exceptions.ConnectionError:
        logger.error("A connection error occurred.")
        raise
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error occurred: {http_err}")
        raise
    except requests.exceptions.RequestException as err:
        logger.error(f"An unexpected error occurred: {err}")
        raise
