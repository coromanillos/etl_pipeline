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

def load_raw_data(raw_file_path: str, logger) -> Optional[dict]:
    if not os.path.exists(raw_file_path):
        logger.error("Raw data file does not exist", file=raw_file_path)
        return None
    try:
        with open(raw_file_path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error("Failed to parse JSON file", file=raw_file_path, error=str(e))
        return None

def transform_series_data(series: dict, required_fields: list, logger) -> tuple[list, list]:
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

def write_failed_log(failed_items: list, log_dir: str, logger) -> None:
    """Save failed transformation items to a timestamped file in processed_data dir."""
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
        logger.warning(
            f"{len(failed_items)} records failed during transformation. Log saved to: {fail_path}",
            failed_count=len(failed_items),
            fail_path=fail_path
        )
    except Exception as e:
        logger.error("Failed to write failed items log", error=str(e), fail_path=fail_path)

def summarize_transformation(total: int, successful: int, failed: int, logger) -> None:
    logger.info(
        "Transformation Summary",
        total_records=total,
        successfully_transformed=successful,
        failed_transformations=failed
    )

def process_raw_data(raw_file_path: str, config: dict, logger) -> Optional[str]:
    """
    Process, validate, and transform raw intraday time series data.
    Returns:
        Path to processed file if successful, else None.
    """
    try:
        raw_data = load_raw_data(raw_file_path, logger)
        if not raw_data:
            logger.error("No raw data loaded; aborting transformation", file=raw_file_path)
            return None

        series = raw_data.get("Time Series (5min)")
        if not series:
            logger.error("Missing 'Time Series (5min)' in data", file=raw_file_path)
            return None

        total_records = len(series)

        processed_data, failed_items = transform_series_data(
            series, config["transform"]["required_fields"], logger
        )

        if not processed_data:
            logger.warning("No valid data processed.")
            return None

        processed_path = save_processed_data(
            processed_data, config["directories"]["processed_data"]
        )
        if not processed_path:
            logger.error("Failed to save processed data file.", directory=config["directories"]["processed_data"])
            return None

        logger.info("Data transformation completed. Processed file saved.", processed_path=processed_path)

        # Use processed_data directory for failed items instead of a non-existent logs directory
        write_failed_log(failed_items, config["directories"]["processed_data"], logger)

        # Log final transformation summary as structured log
        summarize_transformation(
            total=total_records,
            successful=len(processed_data),
            failed=len(failed_items),
            logger=logger
        )
        return processed_path

    except Exception as e:
        logger.exception("Transform pipeline failed with exception", error=str(e))
        return None