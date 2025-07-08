# tests/unit/test_s3_uploader.py
import pytest
from unittest.mock import MagicMock, patch
from src.etl_postgres_to_s3.s3_uploader import generate_s3_key, upload_file_to_s3


def test_generate_s3_key_defaults():
    config = {"s3": {}}
    key = generate_s3_key("users", config)
    assert "archive/users/dt=" in key
    assert key.endswith(".parquet")


def test_generate_s3_key_logs():
    config = {"s3": {"log_path_format": "logs/{table}/dt={date}/{filename}"}}
    key = generate_s3_key("events", config, key_type="logs")
    assert key.startswith("logs/events/dt=")
    assert key.endswith(".parquet")


@patch("src.etl_postgres_to_s3.s3_uploader.get_s3_client")
def test_upload_file_to_s3_success(mock_client_factory):
    mock_client = MagicMock()
    mock_client_factory.return_value = mock_client

    config = {"s3": {}}
    upload_file_to_s3("/tmp/sample.parquet", config, "key", "bucket")

    mock_client.upload_file.assert_called_once_with("/tmp/sample.parquet", "bucket", "key")