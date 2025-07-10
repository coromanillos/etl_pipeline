import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from src.etl_postgres_to_redshift.redshift_loader import (
    create_table_if_not_exists,
    load_data_to_redshift,
)

@pytest.fixture
def mock_config():
    return {
        "redshift": {
            "schema": "test_schema",
            "connection_string": "postgresql://user:pass@localhost:5432/test_db"
        }
    }

@pytest.fixture
def mock_redshift_connection():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    # Prevent KeyError for encoding lookup
    mock_cursor.connection.encoding = "UTF8"
    # Mock mogrify to return bytes-like objects as expected by execute_values
    mock_cursor.mogrify.side_effect = lambda query, args: f"({', '.join(map(str, args))})".encode('utf-8')
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    return mock_conn, mock_cursor


@patch("src.etl_postgres_to_redshift.redshift_loader.get_redshift_connection")
def test_create_table_if_not_exists(mock_get_conn, mock_config, mock_redshift_connection):
    """Test that create_table_if_not_exists runs the SQL and commits."""
    mock_conn, mock_cursor = mock_redshift_connection
    mock_get_conn.return_value.__enter__.return_value = mock_conn

    create_table_if_not_exists("table_x", {"id": "INT"}, mock_config)

    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()

@patch("src.etl_postgres_to_redshift.redshift_loader.get_redshift_connection")
def test_load_data_to_redshift(mock_get_conn, mock_config, mock_redshift_connection):
    """Test loading a DataFrame into Redshift in batches."""
    mock_conn, mock_cursor = mock_redshift_connection
    mock_get_conn.return_value.__enter__.return_value = mock_conn

    df = pd.DataFrame({"id": [1, 2], "name": ["x", "y"]})
    load_data_to_redshift(df, "users", mock_config, batch_size=1)

    assert mock_cursor.execute.call_count >= 1
    mock_conn.commit.assert_called()

@patch("src.etl_postgres_to_redshift.redshift_loader.get_redshift_connection")
def test_load_data_to_redshift_empty_df(mock_get_conn, mock_config, caplog):
    """Test that loading an empty DataFrame logs a warning and does nothing."""
    df = pd.DataFrame()
    load_data_to_redshift(df, "empty_table", mock_config)

    assert "⚠️ No data to load" in caplog.text
