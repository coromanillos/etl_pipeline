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
        redshift_cfg = config["redshift"]
        # Build connection string dynamically
        connection_string = (
            f"postgresql://{redshift_cfg['user']}:{redshift_cfg['password']}@"
            f"{redshift_cfg['host']}:{redshift_cfg['port']}/{redshift_cfg['db']}"
        )
        logger.info("🔗 Connecting to Redshift.")
        return connector_fn(connection_string)
    except Exception as e:
        logger.error(f"❌ Redshift connection failed: {e}", exc_info=True)
        raise
