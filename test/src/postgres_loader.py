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

config = load_config("../config/config.yaml")
logger = get_logger("postgres_loader")

def load_data():
    processed_dir = Path(config["directories"]["processed_data"])
    if not processed_dir.exists():
        logger.error("Processed data directory missing.", directory=str(processed_dir))
        return

    data_file = get_latest_file(processed_dir)
    if not data_file:
        logger.warning("No processed file found.")
        return

    try:
        with open(data_file, "r") as f:
            data = json.load(f)
            logger.info("Processed data file loaded.", file=str(data_file))
    except Exception as e:
        logger.error("Failed to read processed file.", error=str(e))
        return

    records = []
    required = {"timestamp", "open", "high", "low", "close", "volume"}
    for row in data:
        if not required.issubset(row):
            continue
        try:
            records.append(
                IntradayData(
                    timestamp=datetime.fromisoformat(row["timestamp"]),
                    open=float(row["open"]),
                    high=float(row["high"]),
                    low=float(row["low"]),
                    close=float(row["close"]),
                    volume=int(row["volume"]),
                    created_at=datetime.utcnow()
                )
            )
        except Exception:
            continue

    if not records:
        logger.warning("No valid records to insert.")
        return

    try:
        Session = get_db_session()
        with Session() as session:
            session.bulk_save_objects(records)
            session.commit()
        logger.info("Data loaded into PostgreSQL successfully.", count=len(records))
    except Exception as e:
        logger.error("Database insertion failed.", error=str(e))

if __name__ == "__main__":
    logger.info("Starting data load to PostgreSQL...")
    try:
        load_data()
        logger.info("PostgreSQL data load completed.")
    except Exception as e:
        logger.exception("Unexpected failure during PostgreSQL load.")
