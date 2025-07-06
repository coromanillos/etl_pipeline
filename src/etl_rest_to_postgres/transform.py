##############################################
# Title: Alpha Vantage Time Series Data Validation
# Author: Christopher Romanillos
# Description: Validates and transforms intraday time series data
# Date: 2025-05-18 | Version: 3.5 (centralized config and logging)
##############################################

from concurrent.futures import ThreadPoolExecutor
import logging
from src.utils.data_validation import transform_and_validate_data

logger = logging.getLogger(__name__)

def transform_series_data(series: dict, required_fields: list):
    failed_items = []

    def safe_transform(item):
        try:
            return transform_and_validate_data(item[1], required_fields)
        except Exception as e:
            failed_items.append(item)
            return None

    with ThreadPoolExecutor() as executor:
        results = executor.map(safe_transform, series.items())
        processed_data = [r for r in results if r]

    return processed_data, failed_items

def process_raw_data(raw_data: dict, config: dict, required_fields=None):
    try:
        if not raw_data:
            logger.error("No raw data provided to transform.")
            return None, None

        series = raw_data.get("Time Series (5min)")
        if not series:
            logger.error("Missing 'Time Series (5min)' in raw data.")
            return None, None

        required_fields = required_fields or config["transform"]["required_fields"]
        processed_data, failed_items = transform_series_data(series, required_fields)

        if not processed_data:
            logger.warning("No valid data processed.")
            return None, failed_items

        logger.info(f"Data transformation completed: {len(processed_data)} processed, {len(failed_items)} failed.")
        return processed_data, failed_items

    except Exception as e:
        logger.exception(f"Exception during data transformation: {e}")
        return None, None
