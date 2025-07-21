###################################################
# Title: postgres_cleaner.py
# Description: PostgreSQL schema/table management utilities
# Date: 2025-07-21 | Version: 1.2 (Final, autocommit refactor)
###################################################

import logging
from src.utils.db_client import get_postgres_connection


def drop_all_tables(config: dict, logger: logging.Logger = None) -> None:
    schema = config["postgres_loader"]["schema"]

    query = f"""
        DO $$ DECLARE
            r RECORD;
        BEGIN
            FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = '{schema}') LOOP
                EXECUTE 'DROP TABLE IF EXISTS {schema}.' || quote_ident(r.tablename) || ' CASCADE';
            END LOOP;
        END $$;
    """

    with get_postgres_connection(config) as conn:
        with conn.cursor() as cur:
            cur.execute(query)
        conn.commit()

    if logger:
        logger.info(f"✅ Dropped all tables in schema '{schema}'.")


def vacuum_postgres(config: dict, logger: logging.Logger = None) -> None:
    """Perform VACUUM FULL on the PostgreSQL database."""
    conn = get_postgres_connection(config, autocommit=True)
    try:
        with conn.cursor() as cur:
            cur.execute("VACUUM FULL;")
        if logger:
            logger.info("✅ VACUUM FULL executed successfully.")
    finally:
        conn.close()
