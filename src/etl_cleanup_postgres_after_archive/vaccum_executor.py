##############################################
# File: vacuum_executor.py
# Purpose: Performs VACUUM FULL to free up space
##############################################

import logging
from src.utils.postgres_extractor import get_postgres_connection

def vacuum_postgres(config: dict):
    logger = logging.getLogger(__name__)
    database_url = config["postgres_loader"]["connection_string"]

    try:
        with get_postgres_connection(database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("VACUUM FULL;")
                conn.commit()
                logger.info("✅ VACUUM FULL executed successfully.")
    except Exception as e:
        logger.error(f"❌ VACUUM failed: {e}", exc_info=True)