# tests/integration/test_rest_to_s3_pipeline.py

import os
import pytest
import logging
from src.etl_rest_to_postgres.extract import extract_data
from src.etl_rest_to_postgres.transform import process_raw_data
from src.etl_rest_to_postgres.postgres_loader import load_data
from src.utils.postgres_extractor import extract_table_as_df
from src.etl_postgres_to_s3.parquet_converter import convert_to_parquet
from src.etl_postgres_to_s3.s3_uploader import upload_file_to_s3, generate_s3_key
from src.utils.s3_client import get_s3_client

logger = logging.getLogger(__name__)

@pytest.mark.integration
def test_rest_to_s3_pipeline(test_config, clear_table, delete_s3_key):
    table_name = test_config["postgres_loader"]["table"]
    bucket_name = test_config["s3"]["archive_bucket"]

    # STEP 1️⃣ Clean PostgreSQL table
    clear_table(test_config, table_name)

    # STEP 2️⃣ Extract from API -> Postgres
    raw_data = extract_data(test_config)
    assert raw_data is not None, "❌ No data returned from API."

    processed_data, failed_items = process_raw_data(raw_data, test_config)
    assert processed_data and len(processed_data) > 0, "❌ No valid data processed."

    inserted_rows = load_data(processed_data, test_config)
    assert inserted_rows > 0, f"❌ Expected inserted rows > 0, got {inserted_rows}"

    # STEP 3️⃣ Verify data in Postgres
    df = extract_table_as_df(test_config, table_name)
    assert not df.empty, "❌ Postgres table is empty after insertion."

    # STEP 4️⃣ Postgres -> S3
    parquet_path = convert_to_parquet(df, table_name, test_config)
    assert parquet_path and os.path.exists(parquet_path), f"❌ Parquet file not created: {parquet_path}"

    s3_key = generate_s3_key(table_name, test_config)
    upload_file_to_s3(parquet_path, test_config, s3_key, bucket_name)

    # STEP 5️⃣ Verify file exists in S3
    s3_client = get_s3_client(test_config)
    result = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=s3_key)
    assert "Contents" in result, f"❌ Uploaded file not found in S3 at s3://{bucket_name}/{s3_key}"

    # STEP 6️⃣ Cleanup artifacts
    if os.path.exists(parquet_path):
        os.remove(parquet_path)
    delete_s3_key(test_config, s3_key)

