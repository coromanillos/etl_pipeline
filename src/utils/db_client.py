##############################################
# Title: Database Client
# Author: Christopher Romanillos
# Description: Isolated db connection logic
# Date: 2025-07-06 | Version: 2.0
##############################################

import logging
import psycopg2

logger = logging.getLogger(__name__)

def build_postgres_conn_string(cfg: dict) -> str:
    pg = cfg["postgres_loader"]
    return f"postgresql://{pg['user']}:{pg['password']}@{pg['host']}:{pg['port']}/{pg['db']}"

def get_postgres_connection(config: dict, connector_fn=psycopg2.connect):
    try:
        database_url = build_postgres_conn_string(config)
        logger.debug(f"Connecting to PostgreSQL at: {database_url}")
        return connector_fn(database_url)
    except Exception as e:
        logger.error(f"❌ Failed to connect to Postgres: {e}", exc_info=True)
        raise
