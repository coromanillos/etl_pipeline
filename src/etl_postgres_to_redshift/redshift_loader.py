##############################################
# File: redshift_loader.py (Refactored)
# Author: Christopher Romanillos
# Description: Loads PostgreSQL data to Redshift
# Date: 06/23/25
##############################################

import logging
import pandas as pd
from psycopg2.extras import execute_values
from src.utils.redshift_client import get_redshift_connection

logger = logging.getLogger(__name__)

def create_table_if_not_exists(table_name: str, columns: dict, config: dict):
    schema = config["redshift"]["schema"]
    col_defs = ", ".join([f"{col} {dtype}" for col, dtype in columns.items()])
    query = f"""
    CREATE TABLE IF NOT EXISTS {schema}.{table_name} (
        {col_defs}
    );
    """
    try:
        with get_redshift_connection(config) as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                conn.commit()
                logger.info(f"📌 Table {schema}.{table_name} ensured.")
    except Exception as e:
        logger.error(f"❌ Failed to create table {schema}.{table_name}: {e}", exc_info=True)
        raise

def load_data_to_redshift(df: pd.DataFrame, table_name: str, config: dict, batch_size=10000):
    schema = config["redshift"]["schema"]

    if df.empty:
        logger.warning(f"⚠️ No data to load into {schema}.{table_name}.")
        return

    cols = list(df.columns)
    values = [tuple(x) for x in df.to_numpy()]
    insert_query = f"INSERT INTO {schema}.{table_name} ({', '.join(cols)}) VALUES %s"

    try:
        with get_redshift_connection(config) as conn:
            with conn.cursor() as cur:
                for i in range(0, len(values), batch_size):
                    batch = values[i:i+batch_size]
                    execute_values(cur, insert_query, batch)
                    conn.commit()
                    logger.info(f"📦 Inserted rows {i} to {i+len(batch)} into {schema}.{table_name}")
        logger.info(f"✅ Data successfully loaded into {schema}.{table_name}")
    except Exception as e:
        logger.error(f"❌ Failed to load data into {schema}.{table_name}: {e}", exc_info=True)
        raise
