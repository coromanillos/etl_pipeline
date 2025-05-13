#############################################################################
# Title: Alpha Vantage Time Series Data Validation
# Author: Christopher Romanillos
# Description: Validates and transforms intraday time series data
# Date: 11/02/24 | Version: 2.5 
#############################################################################

import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
import os
from utils.logging import get_logger
from utils.utils import load_config
from utils.file_handler import get_latest_file, save_processed_data
from utils.data_validation import transform_and_validate_data

def initialize_pipeline(config_path="../config/config.yaml"):
    config = load_config(config_path)
    log_file = config.get("transform", {}).get("log_file")
    if not log_file:
        raise ValueError("Missing configuration: transform.log_file")
    logger = get_logger("transform", log_file)
    logger.info("Transform pipeline initialized.")
    return config, logger

def process_raw_data(config, logger):
    try:
        raw_file = get_latest_file(config["directories"]["raw_data"])
        if not raw_file:
            logger.error("No raw data file found.")
            return None

        with open(raw_file, "r") as f:
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
            except Exception as e:
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

        save_processed_data(processed_data, config["directories"]["processed_data"])
        logger.info("Data transformation completed successfully.")

        if failed_items:
            fail_path = os.path.join(
                config['directories']['logs'],
                f"failed_items_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            )
            with open(fail_path, "w") as f:
                for item in failed_items:
                    f.write(f"{item}\n")
            logger.warning("Some records failed during transformation.", failed_log=fail_path)

        return processed_data

    except Exception as e:
        logger.error("Transform pipeline failed.", error=str(e))
        return None

if __name__ == "__main__":
    config, logger = initialize_pipeline()
    process_raw_data(config, logger)
