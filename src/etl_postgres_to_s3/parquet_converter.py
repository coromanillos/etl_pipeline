##############################################
# Title: Parquet Converter
# Author: Christopher Romanillos
# Description: Converts DataFrames to Parquet format
# Date: 2025-06-23 | Version: 1.4 (centralized config)
##############################################

import os
import pandas as pd
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def generate_parquet_path(table_name: str, config: dict, timestamp: str = None) -> str:
    processed_data_dir = config["directories"]["processed_data"]
    os.makedirs(processed_data_dir, exist_ok=True)

    if not timestamp:
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

    return os.path.join(processed_data_dir, f"{table_name}_{timestamp}.parquet")

def convert_to_parquet(df: pd.DataFrame, table_name: str, config: dict, timestamp: str = None) -> str:
    output_path = generate_parquet_path(table_name, config, timestamp)
    compression = config.get("transform", {}).get("compression", "snappy")
    try:
        df.to_parquet(output_path, compression=compression, index=False)
        logger.info(f"📁 Parquet saved: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"❌ Failed to convert {table_name} to Parquet: {e}", exc_info=True)
        return ""