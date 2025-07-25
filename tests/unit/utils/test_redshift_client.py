# tests/unit/utils/test_redshift_client.py

import pytest
from unittest.mock import MagicMock, patch
from src.utils.redshift_client import get_redshift_connection


@patch("src.utils.redshift_client.logger")
def test_get_redshift_connection_success(mock_logger):
    """Test successful Redshift connection creation and info logging."""
    mock_connect = MagicMock()
    config = {
        "redshift": {
            "user": "user",
            "password": "pass",
            "host": "host",
            "port": 5439,
            "db": "db"
        }
    }

    conn = get_redshift_connection(config, connector_fn=mock_connect)

    expected_connection_string = "postgresql://user:pass@host:5439/db"
    mock_connect.assert_called_once_with(expected_connection_string)
    assert conn == mock_connect.return_value
    mock_logger.info.assert_called_once_with("🔗 Connecting to Redshift.")


@patch("src.utils.redshift_client.logger")
def test_get_redshift_connection_failure(mock_logger):
    """Test that connection failure raises and logs error."""
    def failing_connect(_):
        raise Exception("connection failed")

    config = {
        "redshift": {
            "user": "user",
            "password": "pass",
            "host": "host",
            "port": 5439,
            "db": "db"
        }
    }

    with pytest.raises(Exception, match="connection failed"):
        get_redshift_connection(config, connector_fn=failing_connect)

    mock_logger.error.assert_called()
