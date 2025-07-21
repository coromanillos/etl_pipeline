# tests/e2e/test_rest_to_s3.py

import pytest
import logging
import pandas as pd
import os

from src.etl_rest_to_postgres.extract import extract_data
from src.etl_rest_to_postgres.transform import process_raw_data
from src.etl_rest_to_postgres.postgres_loader import load_data
from src.utils.postgres_extractor import extract_table_data
from src.etl_postgres_to_redshift.data_transformer import transform_for_redshift
from src.etl_postgres_to_redshift.data_validator import validate_dataframe
from src.etl_postgres_to_redshift.redshift_loader import (
    create_table_if_not_exists,
    load_data_to_redshift
)
from src.utils.redshift_client import get_redshift_connection

logger = logging.getLogger(__name__)

pytestmark = pytest.mark.end_to_end


def test_rest_to_redshift_pipeline(e2e_config, clear_postgres_table, clear_redshift_table):
    """End-to-end test: REST API -> Postgres -> Redshift."""

    table_name = e2e_config["postgres_loader"]["table"]
    redshift_schema = e2e_config["redshift"]["schema"]

    # STEP 1️⃣ Clean Postgres and Redshift
    clear_postgres_table(e2e_config, table_name)
    clear_redshift_table(e2e_config, table_name)

    # STEP 2️⃣ REST API -> Postgres
    raw_data = extract_data(e2e_config)
    assert raw_data is not None, "❌ No data returned from API."

    processed_data, failed_items = process_raw_data(raw_data, e2e_config)
    assert processed_data and len(processed_data) > 0, "❌ No valid data processed."

    inserted_rows = load_data(processed_data, e2e_config)
    assert inserted_rows > 0, f"❌ Expected inserted rows > 0, got {inserted_rows}"

    # STEP 3️⃣ Confirm data in Postgres
    df_postgres = extract_table_data(table_name, e2e_config)
    assert not df_postgres.empty, "❌ Postgres table is empty after insertion."

    # STEP 4️⃣ Postgres -> Redshift
    df_transformed = transform_for_redshift(df_postgres, e2e_config)
    assert isinstance(df_transformed, pd.DataFrame)
    assert not df_transformed.empty, "❌ Transformed DataFrame is empty."

    valid = validate_dataframe(df_transformed, table_name, e2e_config)
    assert valid, "❌ DataFrame validation for Redshift failed."

    col_types = {
        col: (
            "TIMESTAMP" if pd.api.types.is_datetime64_any_dtype(dtype)
            else "FLOAT8" if pd.api.types.is_float_dtype(dtype)
            else "BIGINT" if pd.api.types.is_integer_dtype(dtype)
            else "VARCHAR"
        )
        for col, dtype in zip(df_transformed.columns, df_transformed.dtypes)
    }
    create_table_if_not_exists(table_name, col_types, e2e_config)
    load_data_to_redshift(df_transformed, table_name, e2e_config)

    # STEP 5️⃣ Confirm data in Redshift
    with get_redshift_connection(e2e_config) as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) FROM {redshift_schema}.{table_name};")
            count = cur.fetchone()[0]
            assert count > 0, f"❌ Expected data in Redshift table {table_name}, but found none."

