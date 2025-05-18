##############################################
# Title: Main ETL Script
# Author: Christopher Romanillos
# Description: Extracts, transforms, and loads 
# Alpha Vantage data into the database.
# Date: 12/08/24 | Version: 2.1 (refactored for modern logging)
##############################################

from extract import extract_data
from transform import process_raw_data
from postgres_loader import load_data
from utils.pipeline import initialize_pipeline

def main():
    try:
        config, logger = initialize_pipeline(component_name="main", config_path="../config/config.yaml")
        logger.info("***** ETL script has started! *****")
        logger.info("ETL Process Started")

        # Step 1: Extract
        raw_file_path = extract_data(config, logger)
        if not raw_file_path:
            logger.error("Data extraction failed.")
            return
        logger.info(f"Data extraction successful. File saved at: {raw_file_path}")

        # Step 2: Transform
        processed_file_path = process_raw_data(raw_file_path, config, logger)
        if not processed_file_path:
            logger.error("Data transformation failed.")
            return
        logger.info(f"Data transformation successful. File saved at: {processed_file_path}")

        # Step 3: Load
        load_data(processed_file_path, config, logger)
        logger.info("ETL process completed successfully.")

    except Exception as e:
        logger.exception(f"Fatal error in ETL pipeline: {e}")

if __name__ == "__main__":
    main()