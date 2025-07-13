import pytest
import logging
import pandas as pd
from src.utils.postgres_extractor import extract_table_as_df
from src.etl_postgres_to_redshift.data_transformer import transform_for_redshift
from src.etl_postgres_to_redshift.data_validator import validate_dataframe
from src.etl_postgres_to_redshift.redshift_loader import (
    create_table_if_not_exists,
    load_data_to_redshift
)
from src.utils.redshift_client import get_redshift_connection

logger = logging.getLogger(__name__)

@pytest.mark.integration
def test_postgres_to_redshift_pipeline(test_config, clear_table):
    table_name = test_config["postgres_loader"]["table"]
    redshift_schema = test_config["redshift"]["schema"]

    # STEP 0: Clean target Redshift table before test (if applicable)
    with get_redshift_connection(test_config) as conn:
        with conn.cursor() as cur:
            cur.execute(f"DROP TABLE IF EXISTS {redshift_schema}.{table_name};")
            conn.commit()

    # STEP 1: Extract data from PostgreSQL
    df = extract_table_as_df(test_config, table_name)
    assert not df.empty, "Extracted DataFrame is empty."

    # STEP 2: Transform DataFrame for Redshift compatibility
    df_transformed = transform_for_redshift(df, test_config)
    assert isinstance(df_transformed, pd.DataFrame)
    assert not df_transformed.empty, "Transformed DataFrame is empty."

    # STEP 3: Validate transformed DataFrame before loading
    valid = validate_dataframe(df_transformed, table_name, test_config)
    assert valid, "DataFrame validation failed."

    # STEP 4: Create table in Redshift if it doesn't exist
    # For create_table_if_not_exists, columns dict should map col names to Redshift data types (strings)
    # We can infer column names/types from the DataFrame:
    col_types = {}
    for col, dtype in zip(df_transformed.columns, df_transformed.dtypes):
        if pd.api.types.is_datetime64_any_dtype(dtype):
            col_types[col] = "TIMESTAMP"
        elif pd.api.types.is_float_dtype(dtype):
            col_types[col] = "FLOAT8"
        elif pd.api.types.is_integer_dtype(dtype):
            col_types[col] = "BIGINT"
        else:
            col_types[col] = "VARCHAR"

    create_table_if_not_exists(table_name, col_types, test_config)

    # STEP 5: Load data into Redshift
    try:
        load_data_to_redshift(df_transformed, table_name, test_config)
    except Exception as e:
        pytest.fail(f"Loading data to Redshift failed: {e}")

    # STEP 6: Verify data inserted into Redshift (count rows)
    with get_redshift_connection(test_config) as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) FROM {redshift_schema}.{table_name};")
            count = cur.fetchone()[0]
            assert count > 0, f"Expected data in Redshift table {table_name}, but found none."
