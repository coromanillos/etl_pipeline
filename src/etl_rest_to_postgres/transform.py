#############################################################################
# Title: Alpha Vantage Time Series Data Validation
# Author: Christopher Romanillos
# Description: Validates and transforms intraday time series data
# Date: 2025-05-18 | Version: 3.4 (refactored for robust error handling and consistent returns)
#############################################################################

import json
import os
from datetime import datetime
from threading import Lock
from concurrent.futures import ThreadPoolExecutor
from typing import Optional
from utils.file_handler import save_processed_data
from utils.data_validation import transform_and_validate_data
import logging

logger = logging.getLogger(__name__)

def load_raw_data(raw_file_path: str) -> Optional[dict]:
    if not os.path.exists(raw_file_path):
        logger.error(f"Raw data file does not exist: {raw_file_path}")
        return None
    try:
        with open(raw_file_path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON file {raw_file_path}: {e}")
        return None

def transform_series_data(series: dict, required_fields: list) -> tuple[list, list]:
    processed_data = []
    failed_items = []
    lock = Lock()

    def safe_transform(item):
        try:
            return transform_and_validate_data(item, required_fields)
        except Exception:
            with lock:
                failed_items.append(item)
            return None

    with ThreadPoolExecutor() as executor:
        results = executor.map(safe_transform, series.items())
        processed_data = [r for r in results if r]
    return processed_data, failed_items

def write_failed_log(failed_items: list, log_dir: str) -> None:
    if not failed_items:
        return

    fail_path = os.path.join(
        log_dir,
        f"failed_items_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    )
    try:
        with open(fail_path, "w") as f:
            for item in failed_items:
                f.write(f"{item}\n")
        logger.warning(f"{len(failed_items)} records failed during transformation. Log saved to: {fail_path}")
    except Exception as e:
        logger.error(f"Failed to write failed items log {fail_path}: {e}")

def summarize_transformation(total: int, successful: int, failed: int) -> None:
    logger.info(f"Transformation Summary: Total={total}, Success={successful}, Failed={failed}")

def process_raw_data(raw_file_path: str, config: dict) -> Optional[str]:
    try:
        raw_data = load_raw_data(raw_file_path)
        if not raw_data:
            logger.error(f"No raw data loaded; aborting transformation for {raw_file_path}")
            return None

        series = raw_data.get("Time Series (5min)")
        if not series:
            logger.error(f"Missing 'Time Series (5min)' in data from file: {raw_file_path}")
            return None

        total_records = len(series)

        processed_data, failed_items = transform_series_data(
            series, config["transform"]["required_fields"]
        )

        if not processed_data:
            logger.warning("No valid data processed.")
            return None

        processed_path = save_processed_data(
            processed_data, config["directories"]["processed_data"]
        )
        if not processed_path:
            logger.error(f"Failed to save processed data file in {config['directories']['processed_data']}")
            return None

        logger.info(f"Data transformation completed. Processed file saved: {processed_path}")

        write_failed_log(failed_items, config["directories"]["processed_data"])

        summarize_transformation(
            total=total_records,
            successful=len(processed_data),
            failed=len(failed_items)
        )
        return processed_path

    except Exception as e:
        logger.exception(f"Transform pipeline failed with exception: {e}")
        return None
