##############################################
# Title: postgres_extractor.py
# Author: Christopher Romanillos
# Description: Extracts all PostgreSQL table names
# Date: 06/23/25 
##############################################

import logging
import pandas as pd
import psycopg2
from psycopg2 import sql

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def get_postgres_connection(database_url: str):
    logger.info("Establishing PostgreSQL connection.")
    return psycopg2.connect(database_url)

def get_all_table_names(config: dict, schema: str = None) -> list:
    schema = schema or config["postgres_loader"].get("schema", "public")
    database_url = config["postgres_loader"]["connection_string"]

    query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = %s AND table_type = 'BASE TABLE';
    """
    try:
        with get_postgres_connection(database_url) as conn:
            with conn.cursor() as cur:
                cur.execute(query, (schema,))
                results = cur.fetchall()
                logger.info(f"Fetched {len(results)} tables from schema '{schema}'.")
                return [row[0] for row in results]
    except Exception as e:
        logger.error(f"Failed to retrieve table names: {e}", exc_info=True)
        return []

def extract_table_data(table_name: str, config: dict, schema: str = None) -> pd.DataFrame:
    schema = schema or config["postgres_loader"].get("schema", "public")
    database_url = config["postgres_loader"]["connection_string"]
    try:
        with get_postgres_connection(database_url) as conn:
            query = sql.SQL("SELECT * FROM {}.{}").format(
                sql.Identifier(schema),
                sql.Identifier(table_name)
            )
            logger.info(f"Extracting data from table '{schema}.{table_name}'.")
            return pd.read_sql_query(query, conn)
    except Exception as e:
        logger.error(f"Failed to extract data from {table_name}: {e}", exc_info=True)
        return pd.DataFrame()
