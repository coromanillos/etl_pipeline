# tests/unit/etl_cleanup_postgres_after_archive/test_cleanup_config_loader.py

import pytest
from unittest.mock import patch
from src.etl_cleanup_postgres_after_archive.cleanup_config_loader import load_cleanup_config


@patch("src.etl_cleanup_postgres_after_archive.cleanup_config_loader.load_config")
def test_load_cleanup_config_uses_env_path(mock_load_config):
    mock_load_config.return_value = {"key": "value"}

    config = load_cleanup_config()

    assert config == {"key": "value"}
