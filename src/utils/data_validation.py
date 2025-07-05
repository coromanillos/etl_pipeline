##############################################
# Title: Modular File Handling Script
# Author: Christopher Romanillos
# Description: Modular file handling script with logging support for Docker
# Date: 12/01/24
# Version: 1.5
##############################################

from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def transform_and_validate_data(item, required_fields):
    try:
        timestamp, values = item
        logger.debug(f"Processing data: {timestamp}")

        missing_fields = [field for field in required_fields if field not in values]
        if missing_fields:
            logger.warning(f"Skipping due to missing fields at {timestamp}: {missing_fields}")
            return None

        transformed_data = {
            "timestamp": datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S"),
            "open": float(values["1. open"]),
            "high": float(values["2. high"]),
            "low": float(values["3. low"]),
            "close": float(values["4. close"]),
            "volume": int(values["5. volume"]),
        }

        logger.debug(f"Successfully transformed data: {timestamp}")
        return transformed_data

    except (ValueError, KeyError) as e:
        logger.error(f"Validation error at {timestamp}: {e}", exc_info=True)
        return None