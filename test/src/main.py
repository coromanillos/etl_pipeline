##############################################
# Title: Main ETL Script
# Author: Christopher Romanillos
# Description: Extracts, transforms, and loads 
# Alpha Vantage data into the database.
# Date: 12/08/24
# Version: 1.5
##############################################

from src.utils.logging import setup_logging, get_logger
from extract import extract_data
from transform import initialize_pipeline, process_raw_data
from src.postgres_loader import load_data  

# Step 1: Initialize Logging
setup_logging() 
logger = get_logger(__file__)

def main():
    logger.info("ETL Process Started")

    # Step 2: Extract Data
    extracted_data = extract_data()
    if extracted_data is None:
        logger.error("Data extraction failed. ETL process terminated.")
        return

    # Step 3: Initialize Transformation Pipeline
    try:
        initialize_pipeline()
    except Exception as e:
        logger.exception("Failed to initialize transformation pipeline")
        return

    # Step 4: Transform Data
    transformed_data = process_raw_data(extracted_data)
    if transformed_data is None:
        logger.error("Data transformation failed. ETL process terminated.")
        return

    # Step 5: Load Data into Database
    try:
        load_data()
        logger.info("ETL process completed successfully.")
    except Exception as e:
        logger.exception("Data loading failed")

if __name__ == "__main__":
    main()
