##############################################
# Title: Main ETL Script
# Author: Christopher Romanillos
# Description: Extracts, transforms, and loads 
# Alpha Vantage data into the database.
# Date: 12/08/24
# Version: 1.5
##############################################

from utils.logging import setup_logging, get_logger
from extract import extract_data, initialize_pipeline as initialize_extract_pipeline
from transform import process_raw_data, initialize_pipeline as initialize_transform_pipeline
from postgres_loader import load_data  

# Step 1: Initialize Logging
setup_logging()
fallback_logger = get_logger(__file__)  # renamed to avoid shadowing

def main():
    logger = fallback_logger  # Start with safe logger

    try:
        logger.info("ETL Process Started")

        # Initialize configuration and override logger for extraction
        config, pipeline_logger = initialize_extract_pipeline(config_path="../config/config.yaml")
        logger = pipeline_logger
    except Exception as e:
        logger.error("Failed to initialize extraction pipeline", exc_info=True)
        return

    try:
        # Step 3: Extract Data
        extracted_data = extract_data(config, logger)
        if extracted_data is None:
            logger.error("Data extraction failed. ETL process terminated.")
            return

        # Step 4: Initialize Transformation Pipeline
        try:
            # Use the transformation pipeline initialization here
            config, pipeline_logger = initialize_transform_pipeline(config_path="../config/config.yaml")
            logger = pipeline_logger
        except Exception as e:
            logger.exception("Failed to initialize transformation pipeline")
            return

        # Step 5: Transform Data
        transformed_data = process_raw_data(config, logger)  # Make sure to pass config and logger
        if transformed_data is None:
            logger.error("Data transformation failed. ETL process terminated.")
            return

        # Step 6: Load Data into Database
        try:
            load_data(transformed_data)
            logger.info("ETL process completed successfully.")
        except Exception as e:
            logger.exception("Data loading failed")

    except Exception as e:
        logger.exception("Unhandled error during ETL process")

if __name__ == "__main__":
    main()
