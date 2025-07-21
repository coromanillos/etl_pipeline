# tests/integration/test_postgres_to_s3.py

import pytest
import os
from src.etl_postgres_to_s3.parquet_converter import convert_to_parquet
from src.etl_postgres_to_s3.s3_uploader import upload_file_to_s3, generate_s3_key
from src.utils.postgres_extractor import extract_table_data
from src.utils.aws_client import get_s3_client


@pytest.mark.integration
def test_postgres_to_s3_pipeline(test_postgres_config, clear_postgres_table, delete_s3_key):
    table_name = test_postgres_config["postgres_loader"]["table"]
    bucket_name = test_postgres_config["s3"]["archive_bucket"]

    clear_postgres_table(test_postgres_config, table_name)

    df = extract_table_data(table_name, test_postgres_config)
    assert not df.empty, "Extracted DataFrame is empty."

    parquet_path = convert_to_parquet(df, table_name, test_postgres_config)
    assert parquet_path and os.path.exists(parquet_path), f"Parquet file not created: {parquet_path}"

    s3_key = generate_s3_key(table_name, test_postgres_config)
    upload_file_to_s3(parquet_path, test_postgres_config, s3_key, bucket_name)

    s3_client = get_s3_client(test_postgres_config)
    result = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=s3_key)
    assert "Contents" in result, f"Uploaded file not found in S3 at s3://{bucket_name}/{s3_key}"

    os.remove(parquet_path)
    delete_s3_key(test_postgres_config, s3_key)
