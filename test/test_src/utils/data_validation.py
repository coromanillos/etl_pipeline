##############################################
# Title: Modular File Handling Script
# Author: Christopher Romanillos
# Description: Modular file handling script with logging support for Docker
# Date: 12/01/24
# Version: 1.1
##############################################

import logging
import sys
from datetime import datetime

# Configure logging to send logs to stdout
logging.basicConfig(
    level=logging.INFO,  # Set log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stdout  # Ensures logs go to stdout for Docker to capture
)

def transform_and_validate_data(item, required_fields):
    """Transform and validate data, ensuring required fields exist."""
    try:
        timestamp, values = item
        logging.info(f"Processing data for timestamp {timestamp}.")

        if not all(field in values for field in required_fields):
            logging.warning(f"Missing required fields for timestamp {timestamp}. Skipping entry.")
            return None

        transformed_data = {
            "timestamp": datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S'),
            "open": float(values["1. open"]),
            "high": float(values["2. high"]),
            "low": float(values["3. low"]),
            "close": float(values["4. close"]),
            "volume": int(values["5. volume"]),
        }
        
        logging.info(f"Successfully transformed data for timestamp {timestamp}.")
        return transformed_data

    except (ValueError, KeyError) as e:
        logging.error(f"Error validating data for timestamp {timestamp}: {e}")
        return None
