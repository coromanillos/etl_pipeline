##############################################
# Title: Database Client
# Author: Christopher Romanillos
# Description: Isolated db connection logic
# Date: 2025-07-06 | Version: 2.0
##############################################

import logging
import psycopg2

logger = logging.getLogger(__name__)

def get_postgres_connection(config: dict, connector_fn=psycopg2.connect):
    """
    Returns a Postgres connection using the provided config and optional connector function.
    Supports dependency injection for testing.
    """
    try:
        database_url = config["postgres_loader"]["connection_string"]
        logger.debug(f"Connecting to PostgreSQL at: {database_url}")
        return connector_fn(database_url)
    except Exception as e:
        logger.error(f"❌ Failed to connect to Postgres: {e}", exc_info=True)
        raise
