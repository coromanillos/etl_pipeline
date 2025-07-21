###################################################
# Title: postgres_cleaner.py
# Description: PostgreSQL schema/table management utilities
# Date: 2025-07-20 | Version: 1.0 (Reusable, DRY, Clean)
###################################################

import logging
from src.utils.db_client import get_postgres_connection

def build_postgres_conn_string(cfg: dict) -> str:
    pg = cfg["postgres_loader"]
    return f"postgresql://{pg['user']}:{pg['password']}@{pg['host']}:{pg['port']}/{pg['db']}"

def drop_all_tables(config: dict, logger: logging.Logger = None) -> None:
    schema = config["postgres_loader"]["schema"]
    connection_string = build_postgres_conn_string(config)

    query = f"""
        DO $$ DECLARE
            r RECORD;
        BEGIN
            FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = '{schema}') LOOP
                EXECUTE 'DROP TABLE IF EXISTS {schema}.' || quote_ident(r.tablename) || ' CASCADE';
            END LOOP;
        END $$;
    """

    with get_postgres_connection({"postgres_loader": {"connection_string": connection_string}}) as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            conn.commit()

    if logger:
        logger.info(f"✅ Dropped all tables in schema '{schema}'.")

def vacuum_postgres(config: dict, logger: logging.Logger = None) -> None:
    connection_string = build_postgres_conn_string(config)

    with get_postgres_connection({"postgres_loader": {"connection_string": connection_string}}) as conn:
        with conn.cursor() as cur:
            cur.execute("VACUUM FULL;")
            conn.commit()

    if logger:
        logger.info("✅ VACUUM FULL executed successfully.")
