##############################################
# Title: Data Loading to PostgreSQL Script
# Author: Christopher Romanillos
# Description: Loads cleaned and transformed
# data to PostgreSQL.
# Date: 2025-05-18 | Version: 2.2 (modernized logging, error handling)
##############################################

import json
from datetime import datetime
from utils.schema import IntradayData
from utils.db_connection import get_db_session

def load_data(processed_file_path: str, config: dict, logger) -> int:
    try:
        with open(processed_file_path, "r") as f:
            data = json.load(f)
            logger.info("Processed data file loaded", file=processed_file_path)
    except Exception as e:
        logger.error("Failed to read processed file", file=processed_file_path, error=str(e), exc_info=True)
        return 0

    records = []
    required = {"timestamp", "open", "high", "low", "close", "volume"}
    skipped = 0
    for row in data:
        if not required.issubset(row):
            skipped += 1
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
        except Exception as e:
            skipped += 1
            logger.warning("Skipped row due to parse error", row=row, error=str(e))
            continue

    if not records:
        logger.warning("No valid records to insert.", skipped=skipped)
        return 0

    try:
        Session = get_db_session()
        with Session() as session:
            session.bulk_save_objects(records)
            session.commit()
        logger.info("Data loaded into PostgreSQL successfully.", records_inserted=len(records), skipped=skipped)
        return len(records)
    except Exception as e:
        logger.error("Database insertion failed", error=str(e), exc_info=True)
        return 0