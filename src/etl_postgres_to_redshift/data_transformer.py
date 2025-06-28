##############################################
# Title: data_transformer.py
# Author: Christopher Romanillos
# Description: Transform data for Redshift compatibility
# Date: 06/24/25
##############################################

import pandas as pd
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def transform_for_redshift(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply any transformations needed for Redshift compatibility.
    For example:
    - convert boolean columns to integers
    - enforce datetime format
    - normalize strings
    """
    if df.empty:
        logger.info("Received empty DataFrame — skipping transformation.")
        return df

    bool_cols = df.select_dtypes(include='bool').columns
    for col in bool_cols:
        df[col] = df[col].astype(int)

    # Additional transformations could go here...
    logger.info("✅ Data transformed for Redshift compatibility.")
    return df
