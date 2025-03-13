##############################################
# Title: Main ETL Script
# Author: Christopher Romanillos
# Description: Extracts, transforms, and loads 
# Alpha Vantage data into the database.
# Date: 12/08/24
# Version: 1.3
##############################################

import logging
from pathlib import Path
from extract import extract_data
from transform import initialize_pipeline, process_raw_data
from load import load_data  

# Setup logging for ETL process
log_file = Path(__file__).resolve().parent.parent / 'logs' / 'etl_pipeline.log'
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    logging.info("ETL Process Started")

    # Step 1: Extract Data
    extracted_data = extract_data()
    if extracted_data is None:
        logging.error("Data extraction failed. ETL process terminated.")
        return

    # Step 2: Initialize Transformation Pipeline
    try:
        initialize_pipeline()
    except Exception as e:
        logging.error(f"Failed to initialize transformation pipeline: {e}")
        return

    # Step 3: Transform Data
    transformed_data = process_raw_data(extracted_data)  # Ensure function accepts extracted_data
    if transformed_data is None:
        logging.error("Data transformation failed. ETL process terminated.")
        return

    # Step 4: Load Data into Database
    try:
        load_data()
        logging.info("ETL process completed successfully.")
    except Exception as e:
        logging.error(f"Data loading failed: {e}")

if __name__ == "__main__":
    main()




