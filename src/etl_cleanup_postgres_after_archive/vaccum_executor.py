###############################################
# File: vacuum_executor.py (Refactored)
# Purpose: Performs VACUUM FULL on PostgreSQL
###############################################

from src.utils.postgres_extractor import get_postgres_connection

def vacuum_postgres(config: dict, logger):
    database_url = config["postgres_loader"]["connection_string"]

    try:
        with get_postgres_connection(database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("VACUUM FULL;")
                conn.commit()
                logger.info("✅ VACUUM FULL executed successfully.")
    except Exception as e:
        logger.error(f"❌ VACUUM failed: {e}", exc_info=True)