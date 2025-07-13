# tests/integration/test_rest_to_postgres.py

import pytest
import logging
from src.etl_rest_to_postgres.extract import extract_data
from src.etl_rest_to_postgres.transform import process_raw_data
from src.etl_rest_to_postgres.postgres_loader import load_data
from src.utils.db_client import get_postgres_connection

logger = logging.getLogger(__name__)

@pytest.mark.integration
def test_rest_to_postgres_pipeline(test_config, clear_table):
    # Clean target table before starting test
    clear_table(test_config, "intraday_data")

    # Step 1: Extract raw data from API
    raw_data = extract_data(test_config)
    assert raw_data is not None, "No data returned from API."

    # Step 2: Transform and validate data
    processed_data, failed_items = process_raw_data(raw_data, test_config)
    assert processed_data and len(processed_data) > 0, "No valid data processed."

    # Step 3: Load into PostgreSQL
    inserted_rows = load_data(processed_data, test_config)
    assert inserted_rows > 0, f"Expected inserted rows > 0, got {inserted_rows}"

    # Step 4: Verify inserted data exists in DB
    conn = get_postgres_connection(test_config)
    with conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM intraday_data;")
            count = cur.fetchone()[0]
            assert count >= inserted_rows, f"Expected at least {inserted_rows} rows, got {count}"
