##############################################
# Title: Alpha Vantage Time Series Data Validation
# Author: Christopher Romanillos
# Description: ETL pipeline to validate, process, and store time series data.
# Date: 11/02/24
# Version: 2.0
##############################################
import logging
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from utils.utils import setup_logging, load_config
from utils.file_handler import get_latest_file, save_processed_data
from utils.data_validation import transform_and_validate_data

# Load configuration
config = load_config("../config/config.yaml")

# Ensure required config keys exist
required_keys = ["log_file", "directories", "required_fields"]
for key in required_keys:
    if key not in config:
        logging.error(f"Missing required configuration key: {key}")
        raise ValueError(f"Missing required configuration key: {key}")

# Set up logging
log_file = config.get("log_file", "default_log_file.log")
setup_logging(log_file)

# Main pipeline
def process_raw_data():
    try:
        # Get the latest raw data file
        raw_data_file = get_latest_file(config["directories"]["raw_data"])
        if not raw_data_file:
            raise FileNotFoundError("No raw data files found.")
        
        with open(raw_data_file, 'r') as file:
            raw_data = json.load(file)

        # Extract the time series data
        time_series_data = raw_data.get("Time Series (5min)")
        if not time_series_data:
            raise ValueError("Missing 'Time Series (5min)' in raw data.")

        # Process data with parallelism
        processed_data = [] 
        failed_items = []
        
        def safe_transform(item, required_fields):
            try:
                return transform_and_validate_data(item, required_fields)
            except Exception as e:
                # Log and track failed items
                logging.error(f"Error transforming item {item}: {e}")
                failed_items.append({"item": item, "error": str(e)})
                return None
        
        with ThreadPoolExecutor() as executor:
            results = executor.map(
                lambda item: safe_transform(item, config["required_fields"]),
                time_series_data.items()
            )
            processed_data = [result for result in results if result is not None]

        if not processed_data:
            raise ValueError("No valid data was processed.")

        # Save processed data
        try:
            save_processed_data(processed_data, config["directories"]["processed_data"])
        except Exception as e:
            logging.error(f"Error saving processed data: {e}")
            raise
        
        # Log failed items to a file for review
        if failed_items:
            failed_items_file = f"{config['directories']['logs']}/failed_items_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            with open(failed_items_file, "w") as f:
                for failure in failed_items:
                    f.write(f"{failure}\n")
            logging.warning(f"Some items failed processing. Details saved in {failed_items_file}")
            
        logging.info("All tests passed. ETL pipeline completed successfully.")

    except Exception as e:
        logging.error(f"Pipeline failed: {e}")
        raise

if __name__ == "__main__":
    process_raw_data()