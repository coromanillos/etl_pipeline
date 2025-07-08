import pytest
from unittest.mock import patch, MagicMock
from src.utils.table_cleaner import drop_all_tables

@patch("src.utils.table_cleaner.get_postgres_connection")
def test_drop_all_tables_success(mock_get_conn):
    # Mocks
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_get_conn.return_value.__enter__.return_value = mock_conn
    logger = MagicMock()

    # Test config
    config = {
        "postgres_loader": {
            "schema": "test_schema",
            "connection_string": "postgresql://test_user:test_pass@localhost:5432/test_db"
        }
    }

    # Act
    drop_all_tables(config, logger)

    # Assert
    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()
    logger.info.assert_called_with("✅ Dropped all tables in schema 'test_schema'.")

@patch("src.utils.table_cleaner.get_postgres_connection")
def test_drop_all_tables_failure(mock_get_conn):
    # Mocks that simulate failure
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.execute.side_effect = Exception("boom")
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_get_conn.return_value.__enter__.return_value = mock_conn
    logger = MagicMock()

    # Config
    config = {
        "postgres_loader": {
            "schema": "fail_schema",
            "connection_string": "postgresql://user:pass@localhost:5432/db"
        }
    }

    # Act + Assert
    with pytest.raises(Exception, match="boom"):
        drop_all_tables(config, logger)

    logger.error.assert_called()
