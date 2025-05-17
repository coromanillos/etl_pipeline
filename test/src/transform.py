#############################################################################
# Title: Alpha Vantage Time Series Data Validation
# Author: Christopher Romanillos
# Description: Validates and transforms intraday time series data
# Date: 11/02/24 | Version: 3.0
#############################################################################

import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
import os
from utils.pipeline import initialize_pipeline
from utils.file_handler import save_processed_data
from utils.data_validation import transform_and_validate_data

def process_raw_data(raw_file_path: str, config: dict, logger) -> str | None:
    try:
        if not os.path.exists(raw_file_path):
            logger.error("Raw data file does not exist.", file=raw_file_path)
            return None

        with open(raw_file_path, "r") as f:
            raw_data = json.load(f)

        series = raw_data.get("Time Series (5min)")
        if not series:
            raise ValueError("Missing 'Time Series (5min)' in data.")

        processed_data = []
        failed_items = []
        lock = Lock()

        def safe_transform(item, fields):
            try:
                return transform_and_validate_data(item, fields)
            except Exception:
                with lock:
                    failed_items.append(item)
                return None

        with ThreadPoolExecutor() as executor:
            results = executor.map(
                lambda kv: safe_transform(kv, config["transform"]["required_fields"]),
                series.items()
            )
            processed_data = [r for r in results if r]

        if not processed_data:
            logger.warning("No valid data processed.")
            return None

        processed_path = save_processed_data(processed_data, config["directories"]["processed_data"])
        logger.info("Data transformation completed.", file=processed_path)

        if failed_items:
            fail_path = os.path.join(
                config['directories']['logs'],
                f"failed_items_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            )
            with open(fail_path, "w") as f:
                for item in failed_items:
                    f.write(f"{item}\n")
            logger.warning("Some records failed during transformation.", failed_log=fail_path)

        return processed_path

    except Exception as e:
        logger.error("Transform pipeline failed.", error=str(e))
        return None
