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
import logging

logger = logging.getLogger(__name__)

def load_data(processed_file_path: str, config: dict) -> int:
    try:
        with open(processed_file_path, "r") as f:
            data = json.load(f)
            logger.info(f"Processed data file loaded: {processed_file_path}")
    except Exception as e:
        logger.error(f"Failed to read processed file {processed_file_path}: {e}", exc_info=True)
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
            logger.warning(f"Skipped row due to parse error: {e} | Row: {row}")
            continue

    if not records:
        logger.warning(f"No valid records to insert. Skipped: {skipped}")
        return 0

    try:
        Session = get_db_session()
        with Session() as session:
            session.bulk_save_objects(records)
            session.commit()
        logger.info(f"Data loaded into PostgreSQL successfully. Inserted: {len(records)}, Skipped: {skipped}")
        return len(records)
    except Exception as e:
        logger.error(f"Database insertion failed: {e}", exc_info=True)
        return 0
