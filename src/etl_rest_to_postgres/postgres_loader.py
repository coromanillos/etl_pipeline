##############################################
# Title: Data Loading to PostgreSQL Script
# Author: Christopher Romanillos
# Description: Loads cleaned and transformed
# data to PostgreSQL.
# Date: 2025-05-18 | Version: 2.2 (modernized logging, error handling)
##############################################

from utils.schema import IntradayData
from utils.db_connection import get_db_session
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def load_data(processed_data: list, config: dict) -> int:
    """
    Load processed data (list of dicts) into PostgreSQL.

    Args:
        processed_data (list): List of validated dicts ready for DB insert.
        config (dict): Configuration dictionary.

    Returns:
        int: Number of inserted records.
    """
    if not processed_data:
        logger.warning("No processed data provided to load.")
        return 0

    records = []
    required = {"timestamp", "open", "high", "low", "close", "volume"}
    skipped = 0

    for row in processed_data:
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
