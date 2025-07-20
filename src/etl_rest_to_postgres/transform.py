##############################################
# Title: Alpha Vantage Time Series Data Validation
# Author: Christopher Romanillos
# Description: Validates and transforms intraday time series data
# Date: 2025-05-18 | Version: 3.5 (centralized config and logging)
##############################################

import logging
import yaml
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Tuple, List, Dict, Any
from src.utils.data_validation import transform_and_validate_data

logger = logging.getLogger(__name__)

def load_config(path: str = "config.yaml") -> Optional[Dict[str, Any]]:
    try:
        with open(path, "r") as f:
            config = yaml.safe_load(f)
        logger.info(f"Config loaded successfully from {path}")
        return config
    except Exception as e:
        logger.error(f"Failed to load config from {path}: {e}", exc_info=True)
        return None

def transform_series_data(series: dict, required_fields: list) -> Tuple[List[dict], List[tuple]]:
    failed_items = []

    def safe_transform(item):
        logger.debug(f"Transforming item with timestamp: {item[0]}")
        result = transform_and_validate_data(item, required_fields)
        if result is None:
            logger.warning(f"Validation failed for timestamp: {item[0]}")
            failed_items.append(item)
        return result

    logger.info(f"Starting transformation for {len(series)} items")
    with ThreadPoolExecutor() as executor:
        results = executor.map(safe_transform, series.items())

    processed_data = [r for r in results if r]
    logger.info(f"Transformation complete: {len(processed_data)} valid, {len(failed_items)} failed")
    return processed_data, failed_items

def process_raw_data(raw_data: dict, config: dict, required_fields: Optional[list] = None) -> Tuple[Optional[List[dict]], Optional[List[tuple]]]:
    if not raw_data:
        logger.error("No raw data provided to transform.")
        return None, None

    series = raw_data.get("Time Series (5min)")
    if not series:
        logger.error("Missing 'Time Series (5min)' in raw data.")
        logger.debug(f"Raw data keys: {list(raw_data.keys())}")
        return None, None

    required_fields = required_fields or config.get("transform", {}).get("required_fields", [])
    logger.info(f"Using required fields for validation: {required_fields}")

    try:
        processed_data, failed_items = transform_series_data(series, required_fields)
        if not processed_data:
            logger.warning("No valid data processed.")
            logger.debug(f"Failed items count: {len(failed_items)}")
            if failed_items:
                logger.debug(f"Sample failed timestamps: {[item[0] for item in failed_items[:5]]}")
            return None, failed_items

        logger.info(f"Data transformation completed: {len(processed_data)} processed, {len(failed_items)} failed.")
        return processed_data, failed_items

    except Exception as e:
        logger.exception(f"Exception during data transformation: {e}")
        return None, None


# Example usage inside your DAG or main script:

if __name__ == "__main__":
    import json
    config = load_config()
    if config is None:
        logger.error("Exiting due to config load failure.")
        exit(1)

    # Assume raw_data is fetched from API or test data
    raw_data = {}  # Replace with actual raw_data fetch
    processed, failed = process_raw_data(raw_data, config)
    logger.info(f"Processed items: {processed}")
    logger.info(f"Failed items: {failed}")
