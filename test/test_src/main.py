##############################################
# Title: Main ETL Script
# Author: Christopher Romanillos
# Description: Extracts, transforms, and loads 
# Alpha Vantage data into the database.
# Date: 12/08/24
# Version: 1.4
##############################################

import logging
import sys
from pathlib import Path
from extract import extract_data
from transform import initialize_pipeline, process_raw_data
from load import load_data  

# Define log file path (Ensure this path is mounted in Docker volume)
log_dir = Path(__file__).resolve().parent.parent / 'logs'
log_dir.mkdir(parents=True, exist_ok=True)  # Ensure log directory exists
log_file = log_dir / 'etl_pipeline.log'

# Setup logging for both file and stdout (for Docker logs)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),  # Persist logs in file
        logging.StreamHandler(sys.stdout)  # Output logs to stdout for Docker
    ]
)

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
        logging.exception("Failed to initialize transformation pipeline")
        return

    # Step 3: Transform Data
    transformed_data = process_raw_data(extracted_data)
    if transformed_data is None:
        logging.error("Data transformation failed. ETL process terminated.")
        return

    # Step 4: Load Data into Database
    try:
        load_data()
        logging.info("ETL process completed successfully.")
    except Exception as e:
        logging.exception("Data loading failed")

if __name__ == "__main__":
    main()
