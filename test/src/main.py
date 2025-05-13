##############################################
# Title: Main ETL Script
# Author: Christopher Romanillos
# Description: Extracts, transforms, and loads 
# Alpha Vantage data into the database.
# Date: 12/08/24
# Version: 1.6
##############################################

from extract import extract_data
from transform import process_raw_data
from postgres_loader import load_data
from utils.pipeline import initialize_pipeline

def main():
    try:
        config, logger = initialize_pipeline(component_name="main", config_path="../config/config.yaml")
        logger.info("ETL Process Started")

        # Step 1: Extract
        extracted_data = extract_data(config)
        if extracted_data is None:
            logger.error("Data extraction failed. ETL process terminated.")
            return
        logger.info("Data extraction successful.")

        # Step 2: Transform
        transformed_data = process_raw_data(config)
        if transformed_data is None:
            logger.error("Data transformation failed. ETL process terminated.")
            return
        logger.info("Data transformation successful.")

        # Step 3: Load
        try:
            load_data(transformed_data)
            logger.info("ETL process completed successfully.")
        except Exception as e:
            logger.exception("Data loading failed")

    except Exception as e:
        # Fallback logger in case initialization fails
        print(f"Fatal error in ETL pipeline: {e}")

if __name__ == "__main__":
    main()
