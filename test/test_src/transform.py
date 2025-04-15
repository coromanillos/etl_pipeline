##############################################
# Title: Alpha Vantage Time Series Data Validation
# Author: Christopher Romanillos
# Description: ETL pipeline to validate, process, and store time series data.
# Date: 11/02/24
# Version: 2.3
##############################################

import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from utils.logging import get_logger
from utils.utils import load_config
from utils.file_handler import get_latest_file, save_processed_data
from utils.data_validation import transform_and_validate_data

# Initialize structured logger
logger = get_logger(module_name="transform.py")

# Load configuration
config_path = "../config/config.yaml"
config = load_config(config_path)

def initialize_pipeline(config_path=config_path):
    """
    Loads and validates configuration settings.
    Ensures all required keys exist.
    """
    global config
    config = load_config(config_path)

    required_keys = ["log_file", "directories", "required_fields"]
    for key in required_keys:
        if key not in config:
            logger.error("Missing required configuration key", key=key)
            raise ValueError(f"Missing required configuration key: {key}")

    logger.info("Pipeline initialized successfully")

def process_raw_data():
    """
    Main function to process raw time series data.
    Extracts, transforms, and saves validated data.
    
    Returns:
        list: Processed data if successful, None otherwise.
    """
    if config is None:
        raise RuntimeError("Pipeline not initialized. Call initialize_pipeline() first.")

    try:
        raw_data_file = get_latest_file(config["directories"]["raw_data"])
        if not raw_data_file:
            raise FileNotFoundError("No raw data files found.")

        with open(raw_data_file, 'r') as file:
            raw_data = json.load(file)

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

        with ThreadPoolExecutor() as executor:
            results = executor.map(
                lambda item: safe_transform(item, config["required_fields"]),
                time_series_data.items()
            )
            processed_data = [result for result in results if result is not None]

        if not processed_data:
            logger.warning("No valid data was processed")
            return None

        try:
            save_processed_data(processed_data, config["directories"]["processed_data"])
        except Exception as e:
            logger.error("Error saving processed data", error=str(e))
            return None

        if failed_items:
            failed_items_file = (
                f"{config['directories']['logs']}/failed_items_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
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
    initialize_pipeline()
    process_raw_data()
