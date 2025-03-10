##############################################
# Title: Modular File handling Script
# Author: Christopher Romanillos
# Description: modular utils script
# Date: 12/01/24
# Version: 1.0
##############################################
import logging
from datetime import datetime

def transform_and_validate_data(item, required_fields):
    try:
        timestamp, values = item
        if not all(field in values for field in required_fields):
            logging.warning(f"Missing required fields for timestamp {timestamp}. Skipping entry.")
            return None

        return {
            "timestamp": datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S'),
            "open": float(values["1. open"]),
            "high": float(values["2. high"]),
            "low": float(values["3. low"]),
            "close": float(values["4. close"]),
            "volume": int(values["5. volume"]),
        }
    except (ValueError, KeyError) as e:
        logging.error(f"Error validating data for timestamp {timestamp}: {e}")
        return None