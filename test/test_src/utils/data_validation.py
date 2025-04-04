##############################################
# Title: Modular File Handling Script
# Author: Christopher Romanillos
# Description: Modular file handling script with logging support for Docker
# Date: 12/01/24
# Version: 1.2
##############################################

import structlog
import sys
from datetime import datetime

# Configure structlog for JSON output
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,  # Respects log levels
        structlog.processors.TimeStamper(fmt="iso"),  # Adds timestamp
        structlog.processors.JSONRenderer(),  # Outputs logs in JSON format
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),  # Bridges with logging
    cache_logger_on_first_use=True,
)

# Create structlog logger
logger = structlog.get_logger()

def transform_and_validate_data(item, required_fields):
    """Transform and validate data, ensuring required fields exist."""
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
