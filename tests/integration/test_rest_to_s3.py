# tests/integration/test_postgres_to_s3.py

import pytest
import os
import logging
import pandas as pd
from src.etl_postgres_to_s3.parquet_converter import convert_to_parquet, generate_parquet_path
from src.etl_postgres_to_s3.s3_uploader import upload_file_to_s3, generate_s3_key
from src.utils.postgres_extractor import extract_table_as_df
from src.utils.s3_client import get_s3_client

logger = logging.getLogger(__name__)

@pytest.mark.integration
def test_postgres_to_s3_pipeline(test_config):
    table_name = test_config["postgres_loader"]["table"]

    # STEP 1: Extract data from PostgreSQL
    df = extract_table_as_df(test_config, table_name)
    assert not df.empty, "Extracted DataFrame is empty."

    # STEP 2: Convert to Parquet
    parquet_path = convert_to_parquet(df, table_name, test_config)
    assert parquet_path and os.path.exists(parquet_path), f"Parquet file not created: {parquet_path}"

    # STEP 3: Upload to S3
    s3_key = generate_s3_key(table_name, test_config)
    bucket_name = test_config["s3"]["archive_bucket"]

    upload_file_to_s3(parquet_path, test_config, s3_key, bucket_name)

    # STEP 4: Verify file exists in S3
    s3_client = get_s3_client(test_config)
    result = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=s3_key)

    assert "Contents" in result, f"Uploaded file not found in S3 at {s3_key}"
