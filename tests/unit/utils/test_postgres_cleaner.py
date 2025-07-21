# tests/utils/test_postgres_cleaner.py

import pytest
from unittest.mock import Mock, patch
from src.utils.postgres_cleaner import drop_all_tables, vacuum_postgres


@pytest.fixture
def mock_conn_cursor():
    mock_cursor = Mock()
    mock_conn = Mock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    return mock_conn, mock_cursor


@patch("src.utils.postgres_cleaner.get_postgres_connection")
def test_drop_all_tables_executes_expected_sql(mock_get_conn, mock_conn_cursor):
    mock_conn, mock_cursor = mock_conn_cursor
    mock_get_conn.return_value.__enter__.return_value = mock_conn

    config = {
        "postgres_loader": {
            "schema": "test_schema"
        }
    }

    drop_all_tables(config=config)

    expected_fragment = "DROP TABLE IF EXISTS test_schema."
    executed_query = mock_cursor.execute.call_args[0][0]
    assert expected_fragment in executed_query
    mock_conn.commit.assert_called_once()


@patch("src.utils.postgres_cleaner.get_postgres_connection")
def test_vacuum_postgres_executes_vacuum_full(mock_get_conn):
    mock_conn = Mock()
    mock_cursor = Mock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_get_conn.return_value = mock_conn  # No context manager anymore

    config = {
        "postgres_loader": {
            "connection_string": "fake"
        }
    }

    vacuum_postgres(config=config)

    mock_conn.cursor.assert_called_once()
    mock_cursor.execute.assert_called_once_with("VACUUM FULL;")
    mock_conn.close.assert_called_once()
