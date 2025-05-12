##############################################
# Title: Data Loading to PostgreSQL Script
# Author: Christopher Romanillos
# Description: Validates and loads cleaned and 
# transformed data to data lake.
# Assumes the database from POSTGRES_DATABASE_URL
# already exists.
# Date: 12/08/24
# Version: 1.6
##############################################

import json
from datetime import datetime
from pathlib import Path
from utils.utils import load_config
from utils.schema import IntradayData
from utils.file_handler import get_latest_file
from utils.db_connection import get_db_session
from utils.logging import get_logger

# Load configuration
config = load_config("../config/config.yaml")

# Initialize logger using module-based log file
logger = get_logger(module_name="postgres_loader")

def load_data():
    """Load cleaned JSON data into the Postgres data lake."""
    processed_dir = Path(config["directories"]["processed_data"])

    if not processed_dir.exists() or not processed_dir.is_dir():
        logger.error("Processed data directory does not exist.", directory=str(processed_dir))
        return

    most_recent_file = get_latest_file(processed_dir)
    if not most_recent_file:
        logger.warning("No processed data file found.")
        return

    try:
        with open(most_recent_file, "r") as file:
            data = json.load(file)
            logger.info("Successfully loaded data file.", file=str(most_recent_file))
    except FileNotFoundError:
        logger.error("Data file not found.", file=str(most_recent_file))
        return
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON format in data file.", error=str(e))
        return

    required_keys = {"timestamp", "open", "high", "low", "close", "volume"}
    new_records = []

    for record in data:
        missing_keys = required_keys - record.keys()
        if missing_keys:
            logger.warning("Record missing required fields; skipping.", record=record, missing_keys=list(missing_keys))
            continue

        try:
            new_records.append(
                IntradayData(
                    timestamp=datetime.fromisoformat(record["timestamp"]),
                    open=float(record["open"]),
                    high=float(record["high"]),
                    low=float(record["low"]),
                    close=float(record["close"]),
                    volume=int(record["volume"]),
                    created_at=datetime.utcnow()
                )
            )
        except Exception as e:
            logger.warning("Failed to parse record; skipping.", record=record, error=str(e))

    if not new_records:
        logger.warning("No valid records to insert into the database.")
        return

    try:
        Session = get_db_session()
        with Session() as session:
            session.bulk_save_objects(new_records)
            session.commit()
            logger.info("Data successfully loaded into PostgreSQL.", count=len(new_records))
    except Exception as e:
        logger.error("Failed to save records to the database.", error=str(e))


if __name__ == "__main__":
    logger.info("Starting PostgreSQL data load process...")
    try:
        load_data()
        logger.info("Data load process completed successfully.")
    except Exception:
        logger.exception("Unexpected error occurred during the PostgreSQL load process.")
