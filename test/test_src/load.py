##############################################
# Title: Data Loading Script
# Author: Christopher Romanillos
# Description: Validates and loads cleaned and 
# transformed data to data lake.
# Assumes the database from POSTGRES_DATABASE_URL
# already exists.
# Date: 12/08/24
# Version: 1.4
##############################################

import json
from datetime import datetime
from pathlib import Path
from utils.utils import load_config
from utils.schema import IntradayData
from utils.file_handler import get_latest_file
from utils.db_connection import get_db_session
from utils.logging import get_logger 

# Load the configuration
config = load_config("../config/config.yaml")

# Setup structured logging
log_file_path = Path(config["logging"]["log_file"])
logger = get_logger(module_name="load.py", log_file_path=log_file_path)

def load_data():
    """Load processed JSON data into the database."""
    data_dir = Path(config["directories"]["processed_data"])

    if not data_dir.exists() or not data_dir.is_dir():
        logger.error("Processed data directory does not exist", directory=str(data_dir))
        return

    most_recent_file = get_latest_file(data_dir)
    if not most_recent_file:
        logger.warning("No file found to load.")
        return

    # Load and validate JSON data
    try:
        with open(most_recent_file, 'r') as file:
            data = json.load(file)
            logger.info("Loaded data from file", file=str(most_recent_file))
    except FileNotFoundError:
        logger.error("File not found", file=str(most_recent_file))
        return
    except json.JSONDecodeError as e:
        logger.error("Failed to decode JSON", error=str(e))
        return

    # Validate JSON structure and insert records
    new_records = []
    required_keys = {'timestamp', 'open', 'high', 'low', 'close', 'volume'}
    for record in data:
        missing_keys = required_keys - record.keys()
        if missing_keys:
            logger.warning("Skipping invalid record", record=record, missing_keys=list(missing_keys))
            continue
        try:
            new_records.append(
                IntradayData(
                    timestamp=datetime.fromisoformat(record['timestamp']),
                    open=float(record['open']),
                    high=float(record['high']),
                    low=float(record['low']),
                    close=float(record['close']),
                    volume=int(record['volume']),
                    created_at=datetime.utcnow()
                )
            )
        except Exception as e:
            logger.warning("Failed to process record", record=record, error=str(e))

    # Bulk insert into DB
    try:
        Session = get_db_session()
        with Session() as session:
            session.bulk_save_objects(new_records)
            session.commit()
            logger.info("Data loaded into database", count=len(new_records))
    except Exception as e:
        logger.error("Database operation failed", error=str(e))

if __name__ == "__main__":
    logger.info("Starting data load process...")
    try:
        load_data()
        logger.info("Data load process completed successfully.")
    except Exception as e:
        logger.exception("An unexpected error occurred during the data load process")
