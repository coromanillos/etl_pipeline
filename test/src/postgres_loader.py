##############################################
# Title: Data Loading to PostgreSQL Script
# Author: Christopher Romanillos
# Description: Loads cleaned and transformed 
# data to PostgreSQL.
# Date: 12/08/24
# Version: 2.0
##############################################

import json
from datetime import datetime
from utils.schema import IntradayData
from utils.db_connection import get_db_session

def load_data(processed_file_path: str, config: dict, logger) -> None:
    try:
        with open(processed_file_path, "r") as f:
            data = json.load(f)
            logger.info("Processed data file loaded.", file=processed_file_path)
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
