###############################################
# File: table_cleaner.py (Refactored)
# Purpose: Drops all tables in target PostgreSQL schema
###############################################

import logging
from src.utils.postgres_extractor import get_postgres_connection


def drop_all_tables(config: dict) -> None:
    logger = logging.getLogger("airflow.task.postgres_cleanup")

    schema = config["postgres_loader"].get("schema", "public")
    database_url = config["postgres_loader"]["connection_string"]

    query = f"""
        DO $$ DECLARE
            r RECORD;
        BEGIN
            FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = '{schema}') LOOP
                EXECUTE 'DROP TABLE IF EXISTS {schema}.' || quote_ident(r.tablename) || ' CASCADE';
            END LOOP;
        END $$;
    """

    try:
        with get_postgres_connection(database_url) as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                conn.commit()
                logger.info(f"✅ Dropped all tables in schema '{schema}'.")
    except Exception as e:
        logger.error(f"❌ Failed to drop tables in schema '{schema}': {e}", exc_info=True)
        raise
