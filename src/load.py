##############################################
# Title: Data Loading Script
# Author: Christopher Romanillos
# Description: Validates and loads cleaned and 
# transformed data to data lake.
# Assumes the database from POSTGRES_DATABASE_URL
# already exists.
# Date: 12/08/24
# Version: 1.3
##############################################

# data_load.py
import json
import logging
from datetime import datetime
from pathlib import Path
from utils.utils import setup_logging
from schema import IntradayData
from utils.file_handler import get_latest_file
from db_connection import get_db_session  # Import the function to get a database session

# Setup logging
log_file = Path(__file__).resolve().parent.parent / 'logs' / 'data_load.log'
setup_logging(log_file)

def load_data():
    """Load processed JSON data into the database."""
    data_dir = Path(__file__).parent.parent / 'data' / 'processed_data'

    if not data_dir.exists() or not data_dir.is_dir():
        logging.error(f"Processed data directory does not exist: {data_dir}")
        return

    most_recent_file = get_latest_file(data_dir)
    if not most_recent_file:
        return

    # Load and validate JSON data
    data = []
    try:
        with open(most_recent_file, 'r') as file:
            data = json.load(file)
            logging.info(f"Loaded data from {most_recent_file}.")
    except FileNotFoundError:
        logging.error(f"File not found: {most_recent_file}")
        return
    except json.JSONDecodeError as e:
        logging.error(f"Failed to decode JSON: {e}")
        return

    # Validate JSON structure and insert records
    new_records = []
    required_keys = {'timestamp', 'open', 'high', 'low', 'close', 'volume'}
    for record in data:
        missing_keys = required_keys - record.keys()
        if missing_keys:
            logging.warning(f"Skipping invalid record: {record}. Missing keys: {missing_keys}")
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
            logging.warning(f"Failed to process record: {record}, error: {e}")

    # Bulk insert and handle database errors
    try:
        Session = get_db_session()  # Get the session from the new function
        with Session() as session:
            session.bulk_save_objects(new_records)
            session.commit()
            logging.info(f"Successfully loaded {len(new_records)} records into the database.")
    except Exception as e:
        logging.error(f"Database operation failed: {e}")

if __name__ == "__main__":
    logging.info("Starting data load process...")
    try:
        load_data()
        logging.info("Data load process completed successfully.")
    except Exception as e:
        logging.error(f"An unexpected error occurred during the data load process: {e}")
