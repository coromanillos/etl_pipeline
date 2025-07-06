##################################################
# File: data_transformer.py (Refactored)
# Description: Transforms PostgreSQL data for Redshift
# Author: Christopher Romanillos
# Date: 06/28/25
##################################################

import logging
import pandas as pd
from schema import get_table_column_types

logger = logging.getLogger(__name__)

def transform_for_redshift(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    logger.info("🔄 Transforming DataFrame for Redshift compatibility.")

    if df.empty:
        logger.info("🟡 Skipping transformation — empty DataFrame.")
        return df

    expected_types = get_table_column_types()

    for col, expected_type in expected_types.items():
        if col not in df.columns:
            logger.debug(f"Skipping '{col}' — not in DataFrame.")
            continue

        try:
            if expected_type.__name__ == "DateTime":
                df[col] = pd.to_datetime(df[col], errors="coerce", utc=True)
                logger.debug(f"🕒 '{col}' cast to datetime (UTC).")
            elif expected_type.__name__ == "Float":
                df[col] = pd.to_numeric(df[col], errors="coerce")
                logger.debug(f"🔢 '{col}' cast to float.")
            elif expected_type.__name__ == "BigInteger":
                df[col] = pd.to_numeric(df[col], errors="coerce", downcast="integer")
                logger.debug(f"🔢 '{col}' cast to BigInteger.")
        except Exception as e:
            logger.warning(f"⚠️ Failed to transform '{col}': {e}")

    logger.info("✅ Transformation complete.")
    return df
