##################################################
# File: data_validator.py (Refactored)
# Description: Validates PostgreSQL data before Redshift load
# Author: Christopher Romanillos
# Date: 06/28/25
##################################################

import logging
import pandas as pd
from src.utils.schema import get_required_columns, get_table_column_types

logger = logging.getLogger(__name__)

def validate_dataframe(df: pd.DataFrame, table_name: str, config: dict) -> bool:
    logger.info(f"🔍 Validating data for table: {table_name}")

    if df.empty:
        logger.warning(f"⚠️ DataFrame for '{table_name}' is empty.")
        return False

    required_columns = get_required_columns()
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"❌ Missing columns in '{table_name}': {missing}")

    nulls = df[required_columns].isnull().sum()
    if not nulls[nulls > 0].empty:
        raise ValueError(f"❌ Nulls found in '{table_name}':\n{nulls[nulls > 0]}")

    if "timestamp" in df.columns:
        if not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
            raise TypeError(f"❌ 'timestamp' in '{table_name}' must be datetime.")
        if df["timestamp"].duplicated().any():
            raise ValueError(f"❌ Duplicate timestamps in '{table_name}'.")

    logger.info(f"✅ Data for '{table_name}' passed validation.")
    return True
