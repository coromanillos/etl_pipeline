# tests/unit/test_parquet_converter.py
import os
import pandas as pd
from src.etl_postgres_to_s3.parquet_converter import convert_to_parquet, generate_parquet_path


def test_generate_parquet_path(tmp_path):
    config = {"directories": {"processed_data": str(tmp_path)}}
    path = generate_parquet_path("sales", config, "20240101T000000Z")
    assert path.endswith("sales_20240101T000000Z.parquet")
    assert path.startswith(str(tmp_path))


def test_convert_to_parquet_creates_file(tmp_path):
    df = pd.DataFrame({"id": [1], "value": ["a"]})
    config = {
        "directories": {"processed_data": str(tmp_path)},
        "transform": {"compression": "snappy"},
    }
    path = convert_to_parquet(df, "metrics", config, "20240101T000000Z")
    assert os.path.exists(path)
    assert path.endswith(".parquet")