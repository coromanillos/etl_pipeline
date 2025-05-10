##############################################
# Title: Alpha Vantage Time Series Data Validation
# Author: Christopher Romanillos
# Description: ETL pipeline to validate, process, and store time series data.
# Date: 11/02/24
# Version: 2.4
##############################################

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
    """
    Loads and validates configuration settings.
    Returns validated configuration and logger instance.
    """
    # Load configuration
    config = load_config(config_path)
    
    # Get log file path from config, or default to "../logs/transform.log"
    log_file_path = config["logging"].get("default_transform_log", "../logs/transform.log")
    
    # Ensure the log directory exists
    log_dir = os.path.dirname(log_file_path)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Initialize logger
    logger = get_logger(module_name="transform.py", log_file_path=log_file_path)

    # Validate required keys in config
    required_keys = ["log_file", "directories", "required_fields"]
    for key in required_keys:
        if key not in config:
            logger.error("Missing required configuration key", key=key)
            raise ValueError(f"Missing required configuration key: {key}")

    logger.info("Pipeline initialized successfully")
    return config, logger


def process_raw_data(config, logger):
    """
    Main function to process raw time series data.
    Extracts, transforms, and saves validated data.
    
    Returns:
        list: Processed data if successful, None otherwise.
    """
    try:
        # Get the latest raw data file
        raw_data_file = get_latest_file(config["directories"]["raw_data"])
        if not raw_data_file:
            raise FileNotFoundError("No raw data files found.")

        # Read raw data from the file
        with open(raw_data_file, 'r') as file:
            raw_data = json.load(file)

        # Extract time series data
        time_series_data = raw_data.get("Time Series (5min)")
        if not time_series_data:
            raise ValueError("Missing 'Time Series (5min)' in raw data.")

        processed_data = []
        failed_items = []
        failed_items_lock = Lock()

        def safe_transform(item, required_fields):
            """
            Safely transforms and validates data while handling exceptions.
            Uses a lock to ensure thread-safe logging and failed item tracking.
            """
            try:
                return transform_and_validate_data(item, required_fields)
            except Exception as e:
                with failed_items_lock:
                    logger.error("Error transforming item", error=str(e), item_preview=str(item)[:100])
                    failed_items.append({"item": item, "error": str(e)})
                return None

        # Process data in parallel using ThreadPoolExecutor
        with ThreadPoolExecutor() as executor:
            results = executor.map(
                lambda item: safe_transform(item, config["required_fields"]),
                time_series_data.items()
            )
            processed_data = [result for result in results if result is not None]

        # Check if any valid data was processed
        if not processed_data:
            logger.warning("No valid data was processed")
            return None

        # Save processed data to the specified directory
        try:
            save_processed_data(processed_data, config["directories"]["processed_data"])
        except Exception as e:
            logger.error("Error saving processed data", error=str(e))
            return None

        # Log and save failed items if there are any
        if failed_items:
            failed_items_file = os.path.join(
                config['directories']['logs'],
                f"failed_items_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            )
            with open(failed_items_file, "w") as f:
                for failure in failed_items:
                    f.write(f"{failure}\n")
            logger.warning("Some items failed processing", failed_items_file=failed_items_file)

        logger.info("ETL pipeline completed successfully")
        return processed_data

    except FileNotFoundError as e:
        logger.error("Pipeline error", error=str(e))
        raise
    except ValueError as e:
        logger.error("Pipeline validation error", error=str(e))
        raise
    except Exception as e:
        logger.error("Unexpected pipeline failure", error=str(e))
        return None


if __name__ == "__main__":
    # Initialize pipeline and logger
    config, logger = initialize_pipeline(config_path="../config/config.yaml")
    
    # Process raw data
    process_raw_data(config, logger)
