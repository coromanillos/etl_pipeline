# tests/unit/etl_cleanup_postgres_after_archive/test_cleanup_logger.py

import pytest
from unittest.mock import patch, mock_open, MagicMock
from src.etl_cleanup_postgres_after_archive.cleanup_logger import log_cleanup_summary


@patch("src.etl_cleanup_postgres_after_archive.cleanup_logger.os.makedirs")
@patch("src.etl_cleanup_postgres_after_archive.cleanup_logger.open", new_callable=mock_open)
@patch("src.etl_cleanup_postgres_after_archive.cleanup_logger.datetime")
def test_log_cleanup_summary(mock_datetime, mock_open_file, mock_makedirs):
    config = {"directories": {"logs": "/tmp/test_logs"}}
    mock_datetime.utcnow.return_value.strftime.return_value = "20250628T120000Z"

    log_cleanup_summary(config, "Cleanup complete.")

    mock_open_file.assert_called_once()
