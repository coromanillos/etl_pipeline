##############################################
# Title: parquet_converter.py
# Author: Christopher Romanillos
# Description: Converts PostgreSQL table data
# (as pandas DataFrames) to Parquet
# Date: 06/23/25
##############################################

import os
import pandas as pd
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def generate_parquet_path(table_name: str, config: dict, timestamp: str = None) -> str:
    from datetime import datetime

    processed_data_dir = config["directories"]["processed_data"]
    os.makedirs(processed_data_dir, exist_ok=True)

    if not timestamp:
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

    filename = f"{table_name}_{timestamp}.parquet"
    return os.path.join(processed_data_dir, filename)


def convert_to_parquet(df: pd.DataFrame, table_name: str, config: dict, timestamp: str = None) -> str:
    output_path = generate_parquet_path(table_name, config, timestamp)
    compression = config.get("transform", {}).get("compression", "snappy")
    try:
        df.to_parquet(output_path, compression=compression, index=False)
        logger.info(f"Saved Parquet file: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Failed to convert {table_name} to Parquet: {e}", exc_info=True)
        return ""
