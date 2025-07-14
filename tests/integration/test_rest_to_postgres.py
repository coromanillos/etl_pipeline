# tests/integration/test_rest_to_postgres.py

import pytest
import logging
from src.etl_rest_to_postgres.extract import extract_data
from src.etl_rest_to_postgres.transform import process_raw_data
from src.etl_rest_to_postgres.postgres_loader import load_data
from src.utils.db_client import get_postgres_connection

logger = logging.getLogger(__name__)

@pytest.mark.integration
def test_rest_to_postgres_pipeline(test_rest_config, clear_postgres_table):
    clear_postgres_table(test_rest_config, "intraday_data")

    raw_data = extract_data(test_rest_config)
    assert raw_data is not None, "No data returned from API."

    processed_data, failed_items = process_raw_data(raw_data, test_rest_config)
    assert processed_data and len(processed_data) > 0, "No valid data processed."

    inserted_rows = load_data(processed_data, test_rest_config)
    assert inserted_rows > 0, f"Expected inserted rows > 0, got {inserted_rows}"

    conn = get_postgres_connection(test_rest_config["postgres_loader"])  # Pass postgres_loader section only
    with conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM intraday_data;")
            count = cur.fetchone()[0]
            assert count >= inserted_rows, f"Expected at least {inserted_rows} rows, got {count}"
