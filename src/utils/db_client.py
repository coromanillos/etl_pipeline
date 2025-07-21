###################################################
# Title: Database Client
# Author: Christopher Romanillos
# Description: Isolated db connection logic
# Date: 2025-07-21 | Version: 2.2 (Final, autocommit supported)
###################################################

import logging
from typing import Callable
import psycopg2
from psycopg2.extensions import connection as PGConnection


logger = logging.getLogger(__name__)


def get_postgres_connection(
    config: dict,
    connector_fn: Callable[..., PGConnection] = psycopg2.connect,
    autocommit: bool = False
) -> PGConnection:
    """
    Establishes and returns a PostgreSQL connection.

    Args:
        config (dict): Configuration dictionary containing 'postgres_loader.connection_string'.
        connector_fn (Callable): Optional, allows dependency injection for testing.
        autocommit (bool): If True, connection will be set to autocommit mode.

    Returns:
        PGConnection: A live connection to PostgreSQL.
    """
    try:
        connection_string = config["postgres_loader"]["connection_string"]
        logger.debug("Connecting to PostgreSQL at: %s", connection_string)
        conn = connector_fn(connection_string)
        conn.autocommit = autocommit
        return conn
    except Exception as e:
        logger.error("Failed to connect to PostgreSQL: %s", e, exc_info=True)
        raise
