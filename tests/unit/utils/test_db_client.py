# tests/unit/test_db_client.py

import pytest
from unittest.mock import Mock
from src.utils.db_client import get_postgres_connection


def test_get_postgres_connection_sets_autocommit_false_by_default():
    mock_conn = Mock()
    mock_connector = Mock(return_value=mock_conn)

    config = {
        "postgres_loader": {
            "connection_string": "postgresql://test_user:test_password@localhost:5432/test_db"
        }
    }

    conn = get_postgres_connection(config=config, connector_fn=mock_connector)

    assert conn == mock_conn
    assert conn.autocommit is False
    mock_connector.assert_called_once_with(config["postgres_loader"]["connection_string"])


def test_get_postgres_connection_sets_autocommit_true():
    mock_conn = Mock()
    mock_connector = Mock(return_value=mock_conn)

    config = {
        "postgres_loader": {
            "connection_string": "postgresql://test_user:test_password@localhost:5432/test_db"
        }
    }

    conn = get_postgres_connection(config=config, connector_fn=mock_connector, autocommit=True)

    assert conn == mock_conn
    assert conn.autocommit is True
    mock_connector.assert_called_once_with(config["postgres_loader"]["connection_string"])
