##############################################
# Title: postgres_extractor.py
# Author: Christopher Romanillos
# Description: Extracts all PostgreSQL table names
# and records using .env and config.yaml
# Date: 06/23/25 
##############################################

import os
import pandas as pd
import psycopg2
import yaml
from psycopg2 import sql
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Load YAML config
def load_config(path: str = "config/config.yaml") -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)

CONFIG = load_config()

# Get connection string and schema from config
DATABASE_URL = os.getenv("DATABASE_URL") or CONFIG["postgres_loader"]["connection_string"]
SCHEMA = CONFIG["postgres_loader"].get("schema", "public")


def get_postgres_connection():
    """
    Establishes a psycopg2 connection using DATABASE_URL.
    """
    return psycopg2.connect(DATABASE_URL)


def get_all_table_names(schema: str = SCHEMA) -> list:
    """
    Returns all table names in the specified schema.
    """
    query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = %s AND table_type = 'BASE TABLE';
    """

    with get_postgres_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (schema,))
            results = cur.fetchall()
            return [row[0] for row in results]


def extract_table_data(table_name: str, schema: str = SCHEMA) -> pd.DataFrame:
    """
    Extracts all rows from a table and returns a DataFrame.
    """
    with get_postgres_connection() as conn:
        query = sql.SQL("SELECT * FROM {}.{}").format(
            sql.Identifier(schema),
            sql.Identifier(table_name)
        )
        return pd.read_sql_query(query, conn)
