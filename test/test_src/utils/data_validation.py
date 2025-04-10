##############################################
# Title: Modular File Handling Script
# Author: Christopher Romanillos
# Description: Modular file handling script with logging support for Docker
# Date: 12/01/24
# Version: 1.4
##############################################

from datetime import datetime

# Delayed logger setup to support dynamic logging levels
logger = None

def transform_and_validate_data(item, required_fields):
    """Transform and validate data, ensuring required fields exist."""
    global logger
    if not logger:
        from utils.logging import setup_logging, get_logger
        setup_logging()
        logger = get_logger("data_validation")

    try:
        timestamp, values = item
        logger.info("Processing data", timestamp=timestamp)

        # Check for missing required fields
        missing_fields = [field for field in required_fields if field not in values]
        if missing_fields:
            logger.warning("Skipping entry due to missing fields", timestamp=timestamp, missing_fields=missing_fields)
            return None

        # Transform data
        transformed_data = {
            "timestamp": datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S'),
            "open": float(values["1. open"]),
            "high": float(values["2. high"]),
            "low": float(values["3. low"]),
            "close": float(values["4. close"]),
            "volume": int(values["5. volume"]),
        }

        logger.info("Successfully transformed data", timestamp=timestamp)
        return transformed_data

    except (ValueError, KeyError) as e:
        logger.error("Error validating data", timestamp=timestamp, error=str(e))
        return None
