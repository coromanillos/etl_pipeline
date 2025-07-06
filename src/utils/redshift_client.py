###############################################
# File: redshift_client.py (NEW)
# Description: Redshift client wrapper for testability
# Author: Christopher Romanillos
# Date: 07/05/25
###############################################

import psycopg2
import logging

logger = logging.getLogger(__name__)

def get_redshift_connection(config: dict, connector_fn=psycopg2.connect):
    try:
        connection_string = config["redshift"]["connection_string"]
        logger.info("🔗 Connecting to Redshift.")
        return connector_fn(connection_string)
    except Exception as e:
        logger.error(f"❌ Redshift connection failed: {e}", exc_info=True)
        raise
