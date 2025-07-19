##############################################
# Title: postgres_extractor.py
# Author: Christopher Romanillos
# Description: Extracts PostgreSQL table names and data with safe connection handling
# Date: 06/23/25
##############################################

import logging
from typing import List, Optional, Callable, Dict
import pandas as pd
from psycopg2 import sql
from src.utils.db_client import get_postgres_connection

logger = logging.getLogger(__name__)

def get_all_table_names(
    config: Dict,
    schema: Optional[str] = None,
    conn_factory: Callable = get_postgres_connection
) -> List[str]:
    schema = schema or config.get("postgres_loader", {}).get("schema", "public")

    try:
        with conn_factory(config) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = %s AND table_type = 'BASE TABLE';
                    """,
                    (schema,)
                )
                results = cur.fetchall()
                table_names = [row[0] for row in results]
                logger.info(f"📂 Found {len(table_names)} tables in schema '{schema}'.")
                return table_names
    except Exception as e:
        logger.error(f"❌ Failed to fetch tables from schema '{schema}': {e}", exc_info=True)
        return []

def extract_table_data(
    table_name: str,
    config: Dict,
    schema: Optional[str] = None,
    conn_factory: Callable = get_postgres_connection
) -> pd.DataFrame:
    schema = schema or config.get("postgres_loader", {}).get("schema", "public")

    try:
        with conn_factory(config) as conn:
            query = sql.SQL("SELECT * FROM {}.{};").format(
                sql.Identifier(schema),
                sql.Identifier(table_name)
            )
            logger.info(f"📤 Extracting data from '{schema}.{table_name}'.")
            df = pd.read_sql_query(query, conn)
            logger.info(f"✅ Successfully extracted {len(df)} rows from '{table_name}'.")
            return df
    except Exception as e:
        logger.error(f"❌ Failed to extract data from '{schema}.{table_name}': {e}", exc_info=True)
        return pd.DataFrame()
