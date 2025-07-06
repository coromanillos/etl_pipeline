##############################################
# Title: postgres_extractor.py
# Author: Christopher Romanillos
# Description: Extracts all PostgreSQL table names
# Date: 06/23/25 
############################################## 

import logging
import pandas as pd
from psycopg2 import sql
from src.utils.db_client import get_postgres_connection

logger = logging.getLogger(__name__)

def get_all_table_names(config: dict, schema: str = None, conn_factory=get_postgres_connection) -> list:
    schema = schema or config["postgres_loader"].get("schema", "public")
    try:
        with conn_factory(config) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = %s AND table_type = 'BASE TABLE';
                """, (schema,))
                results = cur.fetchall()
                logger.info(f"📂 Found {len(results)} tables in schema '{schema}'.")
                return [row[0] for row in results]
    except Exception as e:
        logger.error(f"❌ Failed to fetch tables: {e}", exc_info=True)
        return []

def extract_table_data(table_name: str, config: dict, schema: str = None, conn_factory=get_postgres_connection) -> pd.DataFrame:
    schema = schema or config["postgres_loader"].get("schema", "public")
    try:
        with conn_factory(config) as conn:
            query = sql.SQL("SELECT * FROM {}.{};").format(
                sql.Identifier(schema), sql.Identifier(table_name)
            )
            logger.info(f"📤 Extracting data from '{schema}.{table_name}'.")
            return pd.read_sql_query(query, conn)
    except Exception as e:
        logger.error(f"❌ Failed to extract data from {table_name}: {e}", exc_info=True)
        return pd.DataFrame()
