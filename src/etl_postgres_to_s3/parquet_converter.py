##############################################
# Title: parquet_converter.py
# Author: Christopher Romanillos
# Description: Converts PostgreSQL table data
# (as pandas DataFrames) to Parquet
# using config settings.
# Date: 06/23/25
##############################################

import os
import yaml
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Load YAML config
def load_config(path: str = "config/config.yaml") -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)

CONFIG = load_config()

# Directories and Parquet config
PROCESSED_DATA_DIR = CONFIG["directories"]["processed_data"]
COMPRESSION = CONFIG.get("transform", {}).get("compression", "snappy")  # fallback default

# Ensure output directory exists
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)


def generate_parquet_path(table_name: str, timestamp: str = None) -> str:
    """
    Generates a full path for saving the Parquet file based on table name and timestamp.
    """
    if not timestamp:
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    
    filename = f"{table_name}_{timestamp}.parquet"
    return os.path.join(PROCESSED_DATA_DIR, filename)


def convert_to_parquet(df: pd.DataFrame, table_name: str, timestamp: str = None) -> str:
    """
    Converts a DataFrame to Parquet with optional compression.
    Returns the full path to the saved file.
    """
    output_path = generate_parquet_path(table_name, timestamp)
    df.to_parquet(output_path, compression=COMPRESSION, index=False)
    return output_path
