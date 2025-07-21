# tests/integration/test_postgres_to_redshift.py

import pytest
import pandas as pd
from src.utils.postgres_extractor import extract_table_data
from src.etl_postgres_to_redshift.data_transformer import transform_for_redshift
from src.etl_postgres_to_redshift.data_validator import validate_dataframe
from src.etl_postgres_to_redshift.redshift_loader import (
    create_table_if_not_exists,
    load_data_to_redshift
)
from src.utils.redshift_client import get_redshift_connection


@pytest.mark.integration
def test_postgres_to_redshift_pipeline(test_redshift_config, clear_redshift_table):
    table_name = test_redshift_config["redshift"]["table"]
    redshift_schema = test_redshift_config["redshift"]["schema"]

    clear_redshift_table(test_redshift_config, table_name)

    df = extract_table_data(table_name, test_redshift_config)
    assert not df.empty, "Extracted DataFrame is empty."

    df_transformed = transform_for_redshift(df, test_redshift_config)
    assert isinstance(df_transformed, pd.DataFrame)
    assert not df_transformed.empty, "Transformed DataFrame is empty."

    valid = validate_dataframe(df_transformed, table_name, test_redshift_config)
    assert valid, "DataFrame validation failed."

    col_types = {
        col: (
            "TIMESTAMP" if pd.api.types.is_datetime64_any_dtype(dtype)
            else "FLOAT8" if pd.api.types.is_float_dtype(dtype)
            else "BIGINT" if pd.api.types.is_integer_dtype(dtype)
            else "VARCHAR"
        )
        for col, dtype in zip(df_transformed.columns, df_transformed.dtypes)
    }

    create_table_if_not_exists(table_name, col_types, test_redshift_config)

    load_data_to_redshift(df_transformed, table_name, test_redshift_config)

    with get_redshift_connection(test_redshift_config) as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) FROM {redshift_schema}.{table_name};")
            count = cur.fetchone()[0]
            assert count > 0, f"Expected data in Redshift table {table_name}, but found none."
