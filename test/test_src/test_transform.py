##############################################
# Title: Alpha Vantage Time Series Data Validation
# Author: Christopher Romanillos
# Description: ETL pipeline to validate, process, and store time series data.
# Date: 11/02/24
# Version: 2.2
##############################################

import logging
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from threading import Lock  # Ensures thread-safe operations
from utils.utils import setup_logging, load_config
from utils.file_handler import get_latest_file, save_processed_data
from utils.data_validation import transform_and_validate_data

# Load configuration
config = load_config("../config/config.yaml")

def initialize_pipeline(config_path="../config/config.yaml"):
    """
    Loads and validates configuration settings.
    Ensures all required keys exist.
    """
    global config
    config = load_config(config_path)

    required_keys = ["log_file", "directories", "required_fields"]
    for key in required_keys:
        if key not in config:
            logging.error(f"Missing required configuration key: {key}")
            raise ValueError(f"Missing required configuration key: {key}")

    setup_logging(config.get("log_file", "default_log_file.log"))
    logging.info("Pipeline initialized successfully.")

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
        # Get the latest raw data file
        raw_data_file = get_latest_file(config["directories"]["raw_data"])
        if not raw_data_file:
            raise FileNotFoundError("No raw data files found.")

        with open(raw_data_file, 'r') as file:
            raw_data = json.load(file)

        # Extract time series data
        time_series_data = raw_data.get("Time Series (5min)")
        if not time_series_data:
            raise ValueError("Missing 'Time Series (5min)' in raw data.")

        # Process data with parallelism
        processed_data = []
        failed_items = []
        failed_items_lock = Lock()  # Ensures thread safety

        def safe_transform(item, required_fields):
            """
            Safely transforms and validates data while handling exceptions.
            Uses a lock to ensure thread-safe logging and failed item tracking.
            """
            try:
                return transform_and_validate_data(item, required_fields)
            except Exception as e:
                error_message = f"Error transforming item {str(item)[:100]}: {e}"  # Truncate long logs
                with failed_items_lock:
                    logging.error(error_message)
                    failed_items.append({"item": item, "error": str(e)})
                return None

        with ThreadPoolExecutor() as executor:
            results = executor.map(
                lambda item: safe_transform(item, config["required_fields"]),
                time_series_data.items()
            )
            processed_data = [result for result in results if result is not None]

        if not processed_data:
            logging.warning("No valid data was processed.")
            return None  # Return None instead of raising an exception

        # Save processed data
        try:
            save_processed_data(processed_data, config["directories"]["processed_data"])
        except Exception as e:
            logging.error(f"Error saving processed data: {e}")
            return None

        # Log failed items to a file for review
        if failed_items:
            failed_items_file = f"{config['directories']['logs']}/failed_items_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            with open(failed_items_file, "w") as f:
                for failure in failed_items:
                    f.write(f"{failure}\n")
            logging.warning(f"Some items failed processing. Details saved in {failed_items_file}")

        logging.info("ETL pipeline completed successfully.")
        return processed_data  # Return processed data for external use

    except FileNotFoundError as e:
        logging.error(f"Pipeline error: {e}")
        raise  # Raise FileNotFoundError for main.py to handle
    except ValueError as e:
        logging.error(f"Pipeline validation error: {e}")
        raise  # Raise ValueError for main.py to handle
    except Exception as e:
        logging.error(f"Unexpected pipeline failure: {e}")
        return None  # Return None instead of crashing

# Only execute when running the script directly
if __name__ == "__main__":
    initialize_pipeline()
    process_raw_data()
